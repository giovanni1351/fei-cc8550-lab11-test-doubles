from unittest.mock import Mock, call

import pytest

from confirmacao import confirmar


@pytest.fixture
def dependencias():
    return Mock(spec=["cobrar"]), Mock(spec=["enviar"])


@pytest.mark.parametrize("status", ["aprovado", "negado"])
def test_resposta_imediata_nao_repete_cobranca(status, dependencias):
    gateway, email = dependencias
    gateway.cobrar.return_value = status

    resultado = confirmar("pedido-10", 9700, gateway, email)

    assert resultado == status
    gateway.cobrar.assert_called_once_with("pedido-10", 9700)
    if status == "aprovado":
        email.enviar.assert_called_once_with("pedido-10", "pedido confirmado")
    else:
        email.enviar.assert_not_called()


@pytest.mark.parametrize("falhas_antes", [1, 2])
@pytest.mark.parametrize("status_final", ["aprovado", "negado"])
def test_repete_conexao_e_para_ao_receber_status(falhas_antes, status_final, dependencias):
    gateway, email = dependencias
    gateway.cobrar.side_effect = [ConnectionError("offline")] * falhas_antes + [status_final]

    resultado = confirmar("pedido-20", 4000, gateway, email, tentativas=3)

    assert resultado == status_final
    assert gateway.cobrar.call_args_list == [call("pedido-20", 4000)] * (falhas_antes + 1)
    if status_final == "aprovado":
        email.enviar.assert_called_once_with("pedido-20", "pedido confirmado")
    else:
        email.enviar.assert_not_called()


@pytest.mark.parametrize("tentativas", [1, 2, 3, 5])
def test_esgota_limite_avisa_uma_vez_e_propaga_ultima_falha(tentativas, dependencias):
    gateway, email = dependencias
    falhas = [ConnectionError(f"falha-{n}") for n in range(tentativas)]
    gateway.cobrar.side_effect = falhas

    with pytest.raises(ConnectionError) as capturada:
        confirmar("pedido-30", 2500, gateway, email, tentativas=tentativas)

    assert capturada.value is falhas[-1]
    assert gateway.cobrar.call_args_list == [call("pedido-30", 2500)] * tentativas
    email.enviar.assert_called_once_with("pedido-30", "falha na cobranca")


@pytest.mark.parametrize("tentativas", [0, -1])
def test_rejeita_limite_invalido_sem_efeitos(tentativas, dependencias):
    gateway, email = dependencias

    with pytest.raises(ValueError, match="pelo menos 1"):
        confirmar("pedido-40", 1000, gateway, email, tentativas=tentativas)

    gateway.cobrar.assert_not_called()
    email.enviar.assert_not_called()


def test_nao_repete_outros_erros_do_gateway(dependencias):
    gateway, email = dependencias
    erro = ValueError("dados inválidos")
    gateway.cobrar.side_effect = erro

    with pytest.raises(ValueError) as capturada:
        confirmar("pedido-50", 1000, gateway, email)

    assert capturada.value is erro
    gateway.cobrar.assert_called_once_with("pedido-50", 1000)
    email.enviar.assert_not_called()


def test_falha_no_email_nao_cobra_de_novo(dependencias):
    gateway, email = dependencias
    gateway.cobrar.return_value = "aprovado"
    email.enviar.side_effect = ConnectionError("email indisponível")

    with pytest.raises(ConnectionError, match="email indisponível"):
        confirmar("pedido-60", 1000, gateway, email)

    gateway.cobrar.assert_called_once_with("pedido-60", 1000)
    email.enviar.assert_called_once_with("pedido-60", "pedido confirmado")
