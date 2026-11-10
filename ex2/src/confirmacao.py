"""Confirmação de pedido com tentativas limitadas de cobrança."""


def confirmar(pedido, centavos, gateway, email, tentativas=3):
    """Retorna o status do gateway e notifica somente quando necessário.

    Apenas ConnectionError da cobrança é repetido. Falhas no envio de e-mail
    não devem provocar uma nova cobrança de um pedido já aprovado.
    """
    if tentativas < 1:
        raise ValueError("tentativas deve ser pelo menos 1")

    realizadas = 0
    while True:
        realizadas += 1
        try:
            status = gateway.cobrar(pedido, centavos)
        except ConnectionError:
            if realizadas == tentativas:
                email.enviar(pedido, "falha na cobranca")
                raise
            continue

        if status == "aprovado":
            email.enviar(pedido, "pedido confirmado")
        return status
