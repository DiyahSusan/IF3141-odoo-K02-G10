{
    "name": "BETA SISFO Control Center",
    "version": "17.0.1.0.0",
    "summary": "Requirement validation, controlled documents, and audit visibility for PT BETA",
    "description": """
Custom Odoo module for the IF3141 implementation milestone.

This module adds:
- project workspaces
- requirement validation flow between Sales, Engineering, and Project Officer
- controlled document register with revision handling
- audit log visibility for Project Officer and COO
    """,
    "author": "Kelompok G10 K02",
    "license": "LGPL-3",
    "category": "Operations",
    "application": True,
    "depends": ["base", "mail", "crm", "project"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/users.xml",
        "data/sample_data.xml",
        "views/workspace_views.xml",
        "views/folder_views.xml",
        "views/requirement_views.xml",
        "views/document_views.xml",
        "views/audit_views.xml",
        "views/res_users_views.xml",
        "views/change_password_wizard_views.xml",
        "views/menu_views.xml",
        "reports/audit_log_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "beta_sisfo/static/src/css/beta_sisfo.css",
        ],
    },
    "installable": True,
}
