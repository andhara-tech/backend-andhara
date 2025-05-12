"""Module for manage the email sender."""


# Body to for sending emails
def get_email_body(clients: list[tuple[str, str]]) -> str:
    message_html = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            p {
                font-size: 16px;
                line-height: 1.5;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #2c3e50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .no-data {
                text-align: center;
                color: #888;
                font-style: italic;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <p>Estimado equipo,</p>
            <p>A continuación, se presenta la lista de clientes a contactar hoy:</p>
    """
    # Construir el cuerpo dinámico
    if not clients:
        message_html += """
            <p class="no-data">No hay clientes para contactar hoy.</p>
        """
    else:
        message_html += """
            <table>
                <tr>
                    <th>Nombre</th>
                    <th>Teléfono</th>
                </tr>
        """
        for name, phone in clients:
            message_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{phone}</td>
                </tr>
            """
        message_html += "</table>"

    # Cerrar el HTML con un pie de página
    message_html += """
            <div class="footer">
                <p>Este correo fue generado automáticamente por el sistema de gestión de clientes,
                por favor no lo responda.</p>
                <p>© 2025 Andhara Tech</p>
            </div>
        </div>
    </body>
    </html>
    """
    return message_html
