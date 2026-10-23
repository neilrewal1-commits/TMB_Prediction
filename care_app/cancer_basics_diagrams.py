"""Original, accessible SVG illustrations for the learning chapters."""
from html import escape


def box(x, y, title, subtitle, color='#e5f3ef'):
    return f'<rect x="{x}" y="{y}" width="240" height="100" rx="18" fill="{color}"/><text x="{x+120}" y="{y+40}" text-anchor="middle" font-weight="700">{escape(title)}</text><text x="{x+120}" y="{y+68}" text-anchor="middle" font-size="15">{escape(subtitle)}</text>'


def arrow(x, y):
    return f'<path d="M{x} {y}h44" stroke="#346b63" stroke-width="3" marker-end="url(#arrow)"/>'


def illustration(kind):
    titles = {
        'cells': ('Cells and growth control', 'Orderly cells and an irregular growing cluster, shown as a simplified illustration.'),
        'causes': ('How changes can build up', 'Inherited changes, copying errors and some exposures can affect cell growth controls.'),
        'spread': ('How cancer can spread', 'Cells from an original cancer may travel through blood or lymph to another site. This does not happen in every cancer.'),
        'tests': ('Putting the evidence together', 'Symptoms or screening lead to investigations, followed by a diagnosis and assessment of extent.'),
        'care': ('Three parts of cancer care', 'Cancer treatment, symptom relief and daily support can happen together.'),
        'stomach': ('The stomach and its wall', 'A simplified stomach and a wall cross-section with lining, supporting tissue, muscle and outer covering. This diagram does not assign a stage.'),
    }
    title, description = titles[kind]
    if kind == 'cells':
        body = box(20, 25, 'Usual growth controls', 'Cells respond to instructions') + box(600, 25, 'Changed growth controls', 'Some cells keep multiplying', '#fcebdc')
        body += ''.join(f'<circle cx="{x}" cy="{y}" r="14" fill="#368b78"/>' for x in (75, 125, 175, 225) for y in (158, 202))
        body += ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#bd7444" stroke="#fff" stroke-width="2"/>' for x, y, r in [(660,166,19),(688,183,24),(716,155,22),(741,190,26),(772,160,21),(794,191,23),(699,210,18)])
        body += '<text x="430" y="185" text-anchor="middle" font-size="16">Simplified cell patterns</text>'
    elif kind == 'causes':
        body = box(20, 35, 'Sources of change', 'Inherited • copying • exposures') + arrow(270, 85) + box(325, 35, 'DNA changes build up', 'Growth instructions may change') + arrow(575, 85) + box(630, 35, 'Growth control changes', 'May contribute to cancer', '#fcebdc')
        body += '<text x="445" y="190" text-anchor="middle">Risk factors affect chances; they do not predict one person’s outcome.</text>'
    elif kind == 'spread':
        body = box(20, 45, 'Original cancer site', 'Some cells may leave') + arrow(270, 95) + box(325, 45, 'Blood or lymph', 'A possible route to another site') + arrow(575, 95) + box(630, 45, 'Distant site', 'Same original cancer type', '#fcebdc')
        body += '<text x="445" y="200" text-anchor="middle">A possible pathway, not an inevitable sequence or a timeline.</text>'
    elif kind == 'tests':
        body = box(20, 45, 'Reason to investigate', 'Symptoms or screening result') + arrow(270, 95) + box(325, 45, 'Build the evidence', 'Examination • imaging • biopsy') + arrow(575, 95) + box(630, 45, 'Understand the diagnosis', 'Type • extent • relevant markers')
        body += '<text x="445" y="200" text-anchor="middle">The tests needed depend on the situation; a scan alone cannot answer everything.</text>'
    elif kind == 'care':
        body = box(20, 55, 'Treat the cancer', 'Surgery • radiation • medicines') + box(325, 55, 'Relieve symptoms', 'Pain • nausea • other concerns') + box(630, 55, 'Support daily life', 'Food • movement • emotional care')
        body += '<path d="M140 170v20H750v-20M445 170v20" stroke="#346b63" fill="none" stroke-width="3"/><text x="445" y="225" text-anchor="middle">These parts of care can happen together.</text>'
    else:
        body = '<path d="M135 25v55c-50 0-75 35-65 83 12 62 110 75 158 37 38-30 45-80 18-117-19-25-51-25-70-9V25" fill="#fcebdc" stroke="#9a6549" stroke-width="5"/><text x="158" y="150" text-anchor="middle" font-weight="700">Stomach</text>'
        body += '<path d="M270 130H360" stroke="#346b63" stroke-dasharray="6 5" stroke-width="2"/>'
        for y, label, color in [(25,'Inner lining','#f4c99d'),(76,'Supporting tissue','#ecdda9'),(127,'Muscle','#a8cec4'),(178,'Outer covering','#dcebe6')]:
            body += f'<rect x="380" y="{y}" width="450" height="45" rx="7" fill="{color}"/><text x="605" y="{y+29}" text-anchor="middle">{label}</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="basics-title basics-desc" viewBox="0 0 900 260" style="width:100%;display:block;font-family:system-ui,sans-serif;font-size:18px;fill:#183e38"><title id="basics-title">{escape(title)}</title><desc id="basics-desc">{escape(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#346b63"/></marker></defs>{body}</svg>'
