import csv
import io

from odoo import http
from odoo.http import request

try:
    import xlsxwriter
except ImportError:  # pragma: no cover
    xlsxwriter = None


class BetaSisfoExportController(http.Controller):
    def _get_logs(self, ids):
        id_list = [int(value) for value in ids.split(",") if value.strip()] if ids else []
        logs = request.env["beta.audit.log"].sudo().browse(id_list) if id_list else request.env["beta.audit.log"].sudo().search([])
        return logs.exists()

    @http.route("/beta_sisfo/audit/export/csv", type="http", auth="user")
    def export_audit_csv(self, ids=None, **kwargs):
        logs = self._get_logs(ids)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Action Type", "Action", "Document", "Project", "Done By", "Version", "Note"])
        for log in logs:
            writer.writerow(
                [
                    log.action_date or "",
                    log.action_type or "",
                    log.action or "",
                    log.document_id.display_name or log.record_display_name or "",
                    log.project_id.display_name or "",
                    log.user_id.display_name or "",
                    log.version or "",
                    log.note or "",
                ]
            )
        content = output.getvalue()
        headers = [
            ("Content-Type", "text/csv; charset=utf-8"),
            ("Content-Disposition", 'attachment; filename="beta_audit_log.csv"'),
        ]
        return request.make_response(content, headers=headers)

    @http.route("/beta_sisfo/audit/export/xlsx", type="http", auth="user")
    def export_audit_xlsx(self, ids=None, **kwargs):
        logs = self._get_logs(ids)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Audit Log")
        headers = ["Timestamp", "Action Type", "Action", "Document", "Project", "Done By", "Version", "Note"]
        header_format = workbook.add_format({"bold": True, "bg_color": "#3B9FB0", "font_color": "#FFFFFF"})
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        for row, log in enumerate(logs, start=1):
            worksheet.write(row, 0, str(log.action_date or ""))
            worksheet.write(row, 1, log.action_type or "")
            worksheet.write(row, 2, log.action or "")
            worksheet.write(row, 3, log.document_id.display_name or log.record_display_name or "")
            worksheet.write(row, 4, log.project_id.display_name or "")
            worksheet.write(row, 5, log.user_id.display_name or "")
            worksheet.write(row, 6, log.version or "")
            worksheet.write(row, 7, log.note or "")
        worksheet.set_column(0, 7, 24)
        workbook.close()
        headers = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", 'attachment; filename="beta_audit_log.xlsx"'),
        ]
        return request.make_response(output.getvalue(), headers=headers)
