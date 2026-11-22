import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent.parent / 'mockups' / 'design-system' / 'assets' / 'fonts'
SIZE = 512
PNG_SIZE = 1024

# Banneret primitives (design-system/tokens/primitives.json), copied because a standalone image cannot read CSS variables.
INK_900 = '#17120e'
CREAM_50 = '#f0e6d2'
GOLD_400 = '#e8c25a'

ORBIT = (  # lucide:orbit v1.70.0, ISC
	'<path d="M20.341 6.484A10 10 0 0 1 10.266 21.85"/>'
	'<path d="M3.659 17.516A10 10 0 0 1 13.74 2.152"/>'
	'<circle cx="12" cy="12" r="3"/>'
	'<circle cx="19" cy="5" r="2"/>'
	'<circle cx="5" cy="19" r="2"/>'
)


def wordmark_path(text: str, center_x: float, baseline: float, px: float) -> str:
	font = TTFont(FONTS / 'atkinson-hyperlegible-next-semibold.ttf')
	units_per_em = font['head'].unitsPerEm
	cmap = font.getBestCmap()
	glyphs = font.getGlyphSet()
	advances = font['hmtx']
	scale = px / units_per_em
	width = sum(advances[cmap[ord(char)]][0] for char in text) * scale
	pen = SVGPathPen(glyphs, ntos=lambda value: f'{value:.2f}'.rstrip('0').rstrip('.'))
	cursor = center_x - width / 2
	for char in text:
		name = cmap[ord(char)]
		glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
		cursor += advances[name][0] * scale
	return pen.getCommands()


def orbit(x: float, y: float, size: float) -> str:
	return (
		f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
		f'stroke="{GOLD_400}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ORBIT}</svg>'
	)


def document(body: str, title: str) -> str:
	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" role="img">'
		f'<title>{title}</title><rect width="{SIZE}" height="{SIZE}" fill="{INK_900}"/>{body}</svg>\n'
	)


def mark_only() -> str:
	# GitHub crops organisation avatars to a rounded square and shows them down to 20 px, so the mark keeps a wide margin and no text.
	mark_size = 320
	offset = (SIZE - mark_size) / 2
	return document(orbit(offset, offset, mark_size), 'Concord')


def mark_with_wordmark() -> str:
	mark_size = 240
	body = (
		orbit((SIZE - mark_size) / 2, 72, mark_size)
		+ f'<path fill="{CREAM_50}" d="{wordmark_path("Concord", SIZE / 2, 424, 88)}"/>'
	)
	return document(body, 'Concord')


def write_svg_and_png(name: str, svg: str) -> None:
	svg_path = HERE / f'{name}.svg'
	svg_path.write_text(svg)
	png_path = HERE / f'{name}.png'
	subprocess.run(
		['rsvg-convert', '-w', str(PNG_SIZE), '-h', str(PNG_SIZE), str(svg_path), '-o', str(png_path)],
		check=True,
	)


def main() -> None:
	write_svg_and_png('avatar-mark', mark_only())
	write_svg_and_png('avatar-wordmark', mark_with_wordmark())


if __name__ == '__main__':
	main()
