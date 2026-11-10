"""Conversão de frete com a cotação recebida por injeção de dependência."""


class CotacaoIndisponivel(Exception):
    """A dependência de cotação não respondeu a tempo."""


class ConversorFrete:
    def __init__(self, cotacao):
        self.cotacao = cotacao

    def em_centavos_de_real(self, centavos_de_dolar):
        try:
            taxa = self.cotacao.dolar()
        except TimeoutError as erro:
            raise CotacaoIndisponivel("Cotação do dólar indisponível") from erro

        if taxa <= 0:
            raise ValueError("A cotação deve ser maior que zero")

        # Centavos de dólar * reais por dólar = centavos de real.
        # Usa o round do Python: no empate, escolhe o inteiro par.
        return round(centavos_de_dolar * taxa)
