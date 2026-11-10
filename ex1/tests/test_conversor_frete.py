from unittest.mock import Mock

import pytest

from conversor_frete import ConversorFrete, CotacaoIndisponivel


class CotacaoStub:
    """Stub manual: resposta fixa, sem conexão com um serviço externo."""

    def __init__(self, taxa):
        self.taxa = taxa

    def dolar(self):
        return self.taxa


@pytest.mark.parametrize(
    "centavos_de_dolar,taxa,esperado",
    [
        (100, 5.0, 500),
        (150, 5.2, 780),
        (0, 5.0, 0),
        (1, 0.5, 0),   # 0,5 -> 0 (par)
        (3, 0.5, 2),   # 1,5 -> 2 (par)
        (1, 2.5, 2),   # 2,5 -> 2 (par)
        (1, 3.5, 4),   # 3,5 -> 4 (par)
        (3, 1.25, 4),  # 3,75 -> 4
    ],
)
def test_converte_com_stub_manual(centavos_de_dolar, taxa, esperado):
    conversor = ConversorFrete(CotacaoStub(taxa))

    resultado = conversor.em_centavos_de_real(centavos_de_dolar)

    assert resultado == esperado
    assert isinstance(resultado, int)


@pytest.mark.parametrize("taxa", [0, -1, -0.01])
def test_rejeita_cotacao_nao_positiva(taxa):
    conversor = ConversorFrete(CotacaoStub(taxa))

    with pytest.raises(ValueError, match="maior que zero"):
        conversor.em_centavos_de_real(100)


def test_traduz_timeout_preservando_a_causa():
    erro_original = TimeoutError("Serviço demorou demais")
    cotacao = Mock(spec=["dolar"])
    cotacao.dolar.side_effect = erro_original
    conversor = ConversorFrete(cotacao)

    with pytest.raises(CotacaoIndisponivel) as capturada:
        conversor.em_centavos_de_real(100)

    assert capturada.value.__cause__ is erro_original
    cotacao.dolar.assert_called_once_with()
