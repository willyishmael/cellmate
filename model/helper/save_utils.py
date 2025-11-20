import logging
from pathlib import Path
from openpyxl import Workbook

logger = logging.getLogger(__name__)


def copy_values_only(src_wb: Workbook) -> Workbook:
    """Return a new Workbook containing only cell values (no formulas, no relationships)."""
    new_wb = Workbook()
    # remove default created sheet
    try:
        default = new_wb.active
        new_wb.remove(default)
    except Exception:
        pass

    for sheet in src_wb.worksheets:
        tgt = new_wb.create_sheet(title=sheet.title)
        for row in sheet.iter_rows(values_only=True):
            # row is a tuple of values (not cells)
            tgt.append(list(row))
    return new_wb


def save_workbook_with_fallback(src_wb: Workbook, out_path: Path, formatter=None):
    """Try to save workbook; on failure attempt to clear externalReferences, then fallback to value-only copy.

    formatter: optional object with method `format_worksheet(ws)`; if provided, it will be called
    on the workbook's active sheet before saving.
    """
    try:
        if formatter is not None:
            try:
                formatter.format_worksheet(src_wb.active)
            except Exception:
                logger.exception("Formatter failed on source workbook; continuing to save attempt")

        src_wb.save(out_path)
        logger.info("Saved %s", out_path)
        return
    except Exception as exc:
        logger.exception("Initial save failed for %s", out_path)

    # Try to clear externalReferences metadata on package if present
    try:
        pkg = getattr(src_wb, "package", None)
        if pkg is not None and getattr(pkg, "externalReferences", None):
            try:
                pkg.externalReferences = []
                if formatter is not None:
                    try:
                        formatter.format_worksheet(src_wb.active)
                    except Exception:
                        logger.exception("Formatter failed on source workbook after clearing externalReferences")
                src_wb.save(out_path)
                logger.info("Saved %s after clearing externalReferences", out_path)
                return
            except Exception:
                logger.exception("Save after clearing externalReferences also failed for %s", out_path)
    except Exception:
        logger.exception("Error while attempting to inspect/clear package.externalReferences")

    # Final fallback: copy values only and save that workbook
    try:
        new_wb = copy_values_only(src_wb)
        if formatter is not None:
            try:
                formatter.format_worksheet(new_wb.active)
            except Exception:
                logger.exception("Formatter failed on value-only workbook; will still attempt save")
        new_wb.save(out_path)
        logger.warning("Saved value-only copy to %s (formulas/links removed)", out_path)
        return
    except Exception:
        logger.exception("Final fallback (value-only copy) failed for %s", out_path)
        raise
