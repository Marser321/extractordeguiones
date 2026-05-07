import json
import re
from datetime import datetime
from statistics import mean
from typing import Optional

try:
    from services.vault_service import vault_service
except ModuleNotFoundError:
    from backend.services.vault_service import vault_service


class MicrotaskService:
    VERSION = "scriptdna-microtasks-v1"

    GROUPS = {
        "ux_clarity": ("Revisar claridad", "UX clarity", "ux_findings.json"),
        "creative_cleanup": ("Pulir creativos", "Creative cleanup", "creative_cleanup.json"),
        "analysis_refinement": ("Mejorar análisis", "Analysis refinement", "analysis_refinement.json"),
        "brand_memory": ("Actualizar memoria", "Brand memory", "brand_memory_candidates.json"),
        "output_readiness": ("Auditar resultado", "Output readiness", "output_readiness.json"),
    }

    TECHNICAL_MARKERS = ("json", "job", ".env", "sdk", "payload", "traceback", "api_key")
    GENERIC_MARKERS = ("limpio y moderno", "alto contraste", "imagen atractiva", "contenido viral")

    def run(self, brand_name: str, video_id: str, groups: Optional[list[str]] = None) -> dict:
        context = self._load_context(brand_name, video_id)
        selected = [group for group in (groups or list(self.GROUPS)) if group in self.GROUPS]
        results = [self._run_group(group, context) for group in selected]

        report = {
            "microtask_version": self.VERSION,
            "brand_name": brand_name,
            "video_id": video_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "overall_score": round(mean([item["score"] for item in results]), 2) if results else 0,
            "status": self._status_from_score(mean([item["score"] for item in results]) if results else 0, bool(results)),
            "groups": results,
            "next_action": self._next_action(results),
        }

        self._write_report(context, report, results)
        return report

    def read_report(self, brand_name: str, video_id: str) -> dict:
        video_path = vault_service.get_video_path(brand_name, video_id)
        report = vault_service.read_json(video_path / "Analisis" / "Microtasks" / "microtask_report.json")
        if not report:
            raise FileNotFoundError("No hay reporte de pulido para este video.")
        return report

    def _load_context(self, brand_name: str, video_id: str) -> dict:
        video_path = vault_service.get_video_path(brand_name, video_id)
        analysis_dir = video_path / "Analisis"
        creative_dir = analysis_dir / "CreativeLab"
        microtask_dir = analysis_dir / "Microtasks"
        microtask_dir.mkdir(parents=True, exist_ok=True)
        return {
            "brand_name": brand_name,
            "video_id": video_id,
            "video_path": video_path,
            "analysis_dir": analysis_dir,
            "microtask_dir": microtask_dir,
            "script": vault_service.read_file(video_path / "guion_original.txt") or "",
            "analysis": vault_service.read_json(analysis_dir / "full_analysis.json") or {},
            "audit": vault_service.read_json(analysis_dir / "auditoria_contexto.json") or {},
            "creative_pack": vault_service.read_json(creative_dir / "creative_pack.json") or {},
            "wisdom": vault_service.read_json(vault_service.create_brand_structure(brand_name) / "Analisis" / "sabiduria_marca.json") or {},
            "profile": vault_service.get_brand_profile(brand_name),
            "outputs": vault_service.list_outputs(brand_name, video_id),
        }

    def _run_group(self, group: str, context: dict) -> dict:
        if group == "ux_clarity":
            return self._ux_clarity(context)
        if group == "creative_cleanup":
            return self._creative_cleanup(context)
        if group == "analysis_refinement":
            return self._analysis_refinement(context)
        if group == "brand_memory":
            return self._brand_memory(context)
        return self._output_readiness(context)

    def _base_result(self, group: str, score: float, recommendation: str, findings: list[str], action: str) -> dict:
        title, key, _filename = self.GROUPS[group]
        return {
            "group": group,
            "label": title,
            "key": key,
            "status": self._status_from_score(score, bool(findings) or score > 0),
            "score": round(max(0, min(10, score)), 2),
            "recommendation": recommendation,
            "primary_action": action,
            "findings": findings[:8],
        }

    def _ux_clarity(self, context: dict) -> dict:
        findings = []
        creative_text = self._flatten(context["creative_pack"])
        if "|" in creative_text:
            findings.append("Hay etiquetas con listas de opciones; conviene mostrarlas como nombres humanos.")
        if self._has_long_labels(context["creative_pack"]):
            findings.append("Hay labels o títulos largos que deben pasar a detalles desplegables.")
        if any(marker in creative_text.lower() for marker in self.TECHNICAL_MARKERS):
            findings.append("Se detectó lenguaje técnico que no debería dominar la interfaz.")
        score = 9 - len(findings) * 1.6
        return self._base_result(
            "ux_clarity",
            score,
            "Mantener cards compactas y mover texto largo a Ver detalles." if findings else "La experiencia se ve clara para operación.",
            findings,
            "Revisar claridad",
        )

    def _creative_cleanup(self, context: dict) -> dict:
        pack = context["creative_pack"]
        channels = pack.get("channel_packs", []) if isinstance(pack, dict) else []
        findings = []
        if not channels:
            findings.append("Falta pack creativo para revisar.")
        for item in channels:
            if any("|" in str(item.get(key, "")) for key in ("channel", "objective", "asset_type")):
                findings.append("Un creativo contiene placeholders con opciones múltiples.")
                break
        prompts = [item.get("prompt", "") for item in channels if isinstance(item, dict)]
        if prompts and mean([len(prompt.split()) for prompt in prompts]) < 35:
            findings.append("Algunos prompts podrían necesitar más composición, uso y CTA.")
        if any(marker in self._flatten({"prompts": prompts}).lower() for marker in self.GENERIC_MARKERS):
            findings.append("Hay frases creativas genéricas que conviene especificar.")
        score = 8.5 - len(findings) * 1.4
        return self._base_result(
            "creative_cleanup",
            score,
            "Normalizar nombres y revisar prompts marcados antes de copiar." if findings else "Creativos listos para usar o copiar.",
            findings,
            "Pulir creativos",
        )

    def _analysis_refinement(self, context: dict) -> dict:
        audit = context["audit"] or {}
        warnings = audit.get("warnings") or []
        score = float(audit.get("overall_score") or 0)
        findings = warnings[:]
        if not context["analysis"]:
            findings.append("Falta análisis base para refinar.")
        if score and score < 7.5:
            findings.append("El análisis merece una pasada de mejora antes de usarlo como memoria.")
        return self._base_result(
            "analysis_refinement",
            score or (4 if findings else 8),
            "Usar una pasada fuerte solo en las advertencias críticas." if findings else "Análisis suficientemente estable.",
            findings,
            "Mejorar análisis",
        )

    def _brand_memory(self, context: dict) -> dict:
        audit_score = float((context["audit"] or {}).get("overall_score") or 0)
        wisdom = context["wisdom"] or {}
        findings = []
        if audit_score < 7.5:
            findings.append("No promover patrones nuevos hasta subir el score de auditoría.")
        if not wisdom:
            findings.append("Falta sabiduría consolidada para esta marca.")
        score = 8 if audit_score >= 7.5 and wisdom else max(4, audit_score)
        return self._base_result(
            "brand_memory",
            score,
            "Actualizar memoria solo con outputs auditados." if findings else "Memoria de marca lista para alimentar próximos análisis.",
            findings,
            "Actualizar memoria",
        )

    def _output_readiness(self, context: dict) -> dict:
        outputs = context["outputs"] or []
        keys = {item.get("key") for item in outputs}
        required = {"summary", "hooks", "ads", "captions", "visual_prompts", "context_audit", "creative_pack_md"}
        missing = sorted(required - keys)
        findings = [f"Falta recurso: {item.replace('_', ' ')}." for item in missing]
        if len(outputs) < 5:
            findings.append("Hay pocos recursos listos para ejecución.")
        score = 10 - len(findings) * 1.1
        return self._base_result(
            "output_readiness",
            score,
            "Completar recursos faltantes antes de producción." if findings else "Outputs listos para ejecución o revisión final.",
            findings,
            "Auditar resultado",
        )

    def _write_report(self, context: dict, report: dict, results: list[dict]) -> None:
        microtask_dir = context["microtask_dir"]
        vault_service.save_json(microtask_dir, "microtask_report.json", report)
        for result in results:
            filename = self.GROUPS[result["group"]][2]
            vault_service.save_json(microtask_dir, filename, result)

    def _next_action(self, results: list[dict]) -> str:
        if not results:
            return "Ejecutar pulido"
        weakest = sorted(results, key=lambda item: item["score"])[0]
        if weakest["score"] >= 8:
            return "Auditar con modelo fuerte"
        return weakest["primary_action"]

    def _status_from_score(self, score: float, has_data: bool = True) -> str:
        if not has_data:
            return "Sin datos"
        if score >= 8:
            return "Listo"
        if score >= 6:
            return "Necesita revisión"
        return "Mejorando"

    def _has_long_labels(self, data: dict) -> bool:
        if not isinstance(data, dict):
            return False
        for value in self._walk(data):
            text = str(value)
            if len(text) > 80 and re.search(r"channel|asset|objective|label|type", text, re.I):
                return True
        return False

    def _walk(self, value):
        if isinstance(value, dict):
            for child in value.values():
                yield from self._walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from self._walk(child)
        else:
            yield value

    def _flatten(self, value) -> str:
        return json.dumps(value or {}, ensure_ascii=False)


microtask_service = MicrotaskService()
