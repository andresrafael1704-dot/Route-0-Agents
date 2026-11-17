"""
Herramienta de búsqueda de precios y compras en Brasil.
Consulta la API pública de Mercado Livre Brasil (MLB) en vivo para obtener
precios reales, flete gratis y enlaces directos, además de generar búsquedas comparativas.
"""

import requests
import urllib.parse

def buscar_mercado_livre(termo_busca: str, limite: int = 4) -> list:
    """
    Busca productos en tiempo real en Mercado Livre Brasil.
    No requiere API key ni costo.
    """
    termo_enc = urllib.parse.quote(termo_busca)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_enc}&limit={limite}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            resultados = []
            for item in data.get("results", []):
                frete_gratis = "✅ Frete Grátis" if item.get("shipping", {}).get("free_shipping") else "⚠️ Frete Pago"
                resultados.append({
                    "titulo": item.get("title"),
                    "preco": float(item.get("price", 0.0)),
                    "frete": frete_gratis,
                    "link": item.get("permalink"),
                    "origem": "Mercado Livre"
                })
            # Ordenar por precio más barato
            resultados.sort(key=lambda x: x["preco"])
            return resultados
    except Exception as e:
        print(f"Error al buscar en Mercado Livre: {e}")
    
    return []

def generar_links_comparativos(termo_busca: str) -> dict:
    """
    Genera links directos de búsqueda rápida en Shopee y Google Shopping
    para comparar con Mercado Livre.
    """
    termo_enc = urllib.parse.quote(termo_busca)
    return {
        "shopee_link": f"https://shopee.com.br/search?keyword={termo_enc}",
        "google_shopping": f"https://www.google.com.br/search?q={termo_enc}&tbm=shop"
    }

def cotizar_reposicion_insumo(nome_produto: str) -> str:
    """
    Genera un informe completo de cotización comparando las mejores ofertas.
    """
    ofertas_ml = buscar_mercado_livre(nome_produto, limite=5)
    links_extras = generar_links_comparativos(nome_produto)

    relatorio = f"🔍 **COTAÇÃO EM TEMPO REAL: {nome_produto.upper()}**\n\n"

    if ofertas_ml:
        relatorio += "📦 **Melhores Ofertas no Mercado Livre (Brasil):**\n"
        for i, item in enumerate(ofertas_ml[:3], 1):
            relatorio += (
                f"{i}. **R$ {item['preco']:.2f}** ({item['frete']})\n"
                f"   *{item['titulo']}*\n"
                f"   🔗 [Ver Produto no ML]({item['link']})\n\n"
            )
    else:
        relatorio += "⚠️ *Não foi possível puxar itens automáticos da API do ML no momento.*\n\n"

    relatorio += "🌐 **Comparar em outras plataformas:**\n"
    relatorio += f"• 🛒 [Buscar na Shopee Brasil]({links_extras['shopee_link']})\n"
    relatorio += f"• 🔎 [Ver no Google Shopping Brasil]({links_extras['google_shopping']})\n"

    return relatorio
