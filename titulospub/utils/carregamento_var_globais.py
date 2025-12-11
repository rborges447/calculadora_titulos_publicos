def _carregar_feriados_se_necessario(feriados):
    """
    Se feriados for None, busca do orquestrador.
    """
    if feriados is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        feriados = vm.get_feriados()
    return feriados

def _carrecar_ipca_dict_se_necessario(ipca_dict):
    """
    Se ipca_dict for None, busca do orquestrador.
    """
    if ipca_dict is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        ipca_dict = vm.get_ipca_dict()
    return ipca_dict

def _carrecar_cdi_se_necessario(cdi):
    """
    Se ipca_dict for None, busca do orquestrador.
    """
    if cdi is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        cdi = vm.get_cdi()
    return cdi

def _carregar_vna_lft_se_necessario(vna_lft):
    """
    Se vna_lft for None, busca do orquestrador.
    """
    if vna_lft is None:
        from titulospub.dados.orquestrador import VariaveisMercado
        vm = VariaveisMercado()
        vna_lft = vm.get_vna_lft()
    return vna_lft