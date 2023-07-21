# coding=utf-8
from java.awt import Color

node_cmap = {
    "other": Color(0.78, 0.53, 0.91),
    "nonbanking": Color(0.37, 0.78, 0.07),
    "bank": Color(0.0, 0.79, 1.0),
    "insurance": Color(0.92, 0.53, 0.08),
    "utilities": Color(0.96, 0.95, 0.0),
    "government": Color(1.0, 0.36, 0.51),
}

label_corrections = {
    "72080043": u"Finanční úřad",
    "6963": u"ČSSZ",
    "1350": u"ČSOB",
    "41197518": u"VZP",
    "4484843": u"Národní rozvojová banka",
    "45317054": u"Komerční banka",
    "45244782": u"Česká spořitelna",
}

NODE_SIZE_RANGE = (0.1, 20)
NODE_TEXT_SIZE_RANGE = (0.1, 15)

def rescale(value, to_range):
    return to_range[0] + value * (to_range[1] - to_range[0])

def attr_as_map(node):
    return {
        "pagerank": node.getAttribute("4"),
        "type": node.getAttribute("3"),
        "label": node.getAttribute("1"),
    }

nodes = list(g.nodes)
max_pr = max(map(lambda node: attr_as_map(node.getNode())["pagerank"], nodes))
for node in nodes:
    node_data = node.getNode()
    attr = attr_as_map(node_data)
    node.color = node_cmap.get(attr["type"], black)
    node.label = attr["label"]

    corr = label_corrections.get(node_data.getId())
    if corr:
        node.label = corr
    
    rel_pr = attr["pagerank"] / max_pr
    node.size = rescale(rel_pr, NODE_SIZE_RANGE)
    
    tp = node_data.getTextProperties()
    tp.size = min(rescale(rel_pr, NODE_TEXT_SIZE_RANGE), 15)
    tp.setDimensions(0,0)

# runLayout(ForceAtlas2, 500)
setVisible(g.filter(degree > 20))