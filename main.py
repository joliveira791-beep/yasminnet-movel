import flet as ft
import random
import string
import routeros_api

def main(page: ft.Page):
    page.title = "YasminNET Móvel"
    page.bgcolor = "#F9F9F9"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Armazenamento de variáveis na memória do App
    ultimo_codigo = ""
    ultima_validade = ""

    # Campos de Configuração
    txt_ip = ft.TextField(label="IP do MikroTik", value="192.168.10.1", text_align=ft.TextAlign.CENTER)
    txt_pass = ft.TextField(label="Senha do Winbox", password=True, can_reveal_password=True, text_align=ft.TextAlign.CENTER)
    txt_mac = ft.TextField(label="MAC da Impressora Bluetooth", value="00:11:22:33:44:55", text_align=ft.TextAlign.CENTER)

    # Campo de tempo visível
    txt_tempo = ft.TextField(value="02:00:00", font_size=22, text_align=ft.TextAlign.CENTER, width=160, read_only=True)
    lbl_resultado = ft.Text("Aguardando comando...", size=16, weight=ft.FontWeight.BOLD, color="#2D2D2D", text_align=ft.TextAlign.CENTER)

    def definir_tempo(e, tempo):
        txt_tempo.value = tempo
        page.update()

    def abrir_config(e):
        page.dialog = modal_cfg
        modal_cfg.open = True
        page.update()

    def salvar_config(e):
        modal_cfg.open = False
        page.update()
        page.show_snack_bar(ft.SnackBar(ft.Text("Configurações salvas no aparelho!")))

    def criar_voucher(e):
        nonlocal ultimo_codigo, ultima_validade
        tempo_limite = txt_tempo.value
        voucher_id = ''.join(random.choices(string.digits, k=6))
        lbl_resultado.value = "Conectando ao MikroTik..."
        page.update()

        try:
            connection = routeros_api.RouterOsApiPool(txt_ip.value, username="admin", password=txt_pass.value, plaintext_login=True)
            api = connection.get_api()
            hotspot_users = api.get_resource('/ip/hotspot/user')
            hotspot_users.add(server="all", name=voucher_id, password=voucher_id, profile="default", limit_uptime=tempo_limite)
            connection.disconnect()

            ultimo_codigo = voucher_id
            ultima_validade = tempo_limite
            btn_imprimir.disabled = False
            
            lbl_resultado.color = "#E50914"
            lbl_resultado.value = f"VOUCHER GERADO COM SUCESSO!\n\nCÓDIGO: {voucher_id}\nVALIDADE: {tempo_limite}"
        except Exception as erro:
            lbl_resultado.color = "#E50914"
            lbl_resultado.value = f"Falha na Conexão!\nVerifique a engrenagem.\nErro: {erro}"
        page.update()

    def imprimir_voucher(e):
        lbl_resultado.value = "Enviando para a impressora..."
        page.update()
        try:
            import socket
            server_address = (txt_mac.value, 1)
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.connect(server_address)
            cupom = (
                "================================\n"
                "      YASMINNET PROVEDOR        \n"
                "       CONEXAO HOTSPOT          \n"
                "================================\n\n"
                f" CODIGO DE ACESSO: {ultimo_codigo}\n"
                f" VALIDADE: {ultima_validade}\n\n"
                " Insira este codigo nos campos  \n"
                " USUARIO e SENHA na tela do     \n"
                " seu celular para conectar.     \n\n"
                "  Obrigado por usar nossa rede! \n"
                "================================\n\n\n\n"
            )
            sock.send(cupom.encode('utf-8'))
            sock.close()
            lbl_resultado.value = f"VOUCHER IMPRESSO!\nCódigo: {ultimo_codigo}"
        except Exception as err:
            lbl_resultado.value = f"Erro na Impressora Bluetooth!\nVerifique o MAC pareado.\nErro: {err}"
        page.update()

    # Modal Flutuante de Configuração Profissional
    modal_cfg = ft.AlertDialog(
        title=ft.Text("Configurações do Roteador", color="#E50914", weight=ft.FontWeight.BOLD),
        content=ft.Column([txt_ip, txt_pass, txt_mac], tight=True, spacing=10),
        actions=[ft.TextButton("SALVAR", on_click=salvar_config, style=ft.ButtonStyle(color="white", bgcolor="#E50914"))],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    btn_imprimir = ft.ElevatedButton("🖨️ IMPRIMIR VOUCHER ATUAL", bgcolor="#1A1A1A", color="white", disabled=True, on_click=imprimir_voucher, height=50)

    # Montagem Visual da Tela Móvel
    page.add(
        ft.Column([
            ft.Text("YasminNET Provedor", size=28, weight=ft.FontWeight.BOLD, color="#E50914", text_align=ft.TextAlign.CENTER),
            ft.Text("Tempo de validade da internet:", size=14, color="#1A1A1A"),
            txt_tempo,
            ft.Row([
                ft.ElevatedButton("1 Hora", bgcolor="#2D2D2D", color="white", on_click=lambda e: definir_tempo(e, "01:00:00")),
                ft.ElevatedButton("2 Horas", bgcolor="#2D2D2D", color="white", on_click=lambda e: definir_tempo(e, "02:00:00")),
                ft.ElevatedButton("1 Dia", bgcolor="#2D2D2D", color="white", on_click=lambda e: definir_tempo(e, "24:00:00")),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.ElevatedButton("GERAR NOVO VOUCHER", bgcolor="#E50914", color="white", on_click=criar_voucher, height=55),
            btn_imprimir,
            ft.Container(lbl_resultado, alignment=ft.alignment.center, padding=10),
            ft.IconButton(icon=ft.icons.SETTINGS, icon_color="gray", on_click=abrir_config, tooltip="Configurações")
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )

ft.app(target=main)
