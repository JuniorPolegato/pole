#!/usr/bin/env python
# -*- coding: utf-8 -*-

pt = 1
inch = 72
mm = inch / 25.4
cm = mm * 10

A0  = (841 * mm, 1189 * mm)
A1  = (594 * mm,  841 * mm)
A2  = (420 * mm,  594 * mm)
A3  = (297 * mm,  420 * mm)
A4  = (210 * mm,  297 * mm)
A5  = (148 * mm,  210 * mm)
A6  = (105 * mm,  148 * mm)
A7  = ( 74 * mm,  105 * mm)
A8  = ( 52 * mm,   74 * mm)
A9  = ( 37 * mm,   52 * mm)
A10 = ( 26 * mm,   37 * mm)

B0  = (1000 * mm, 1414 * mm)
B1  = ( 707 * mm, 1000 * mm)
B2  = ( 500 * mm,  707 * mm)
B3  = ( 353 * mm,  500 * mm)
B4  = ( 250 * mm,  353 * mm)
B5  = ( 176 * mm,  250 * mm)
B6  = ( 125 * mm,  176 * mm)
B7  = (  88 * mm,  125 * mm)
B8  = (  62 * mm,   88 * mm)
B9  = (  44 * mm,   62 * mm)
B10 = (  31 * mm,   44 * mm)

C0  = (917 * mm, 1297 * mm)
C1  = (648 * mm,  917 * mm)
C2  = (458 * mm,  648 * mm)
C3  = (324 * mm,  458 * mm)
C4  = (229 * mm,  324 * mm)
C5  = (162 * mm,  229 * mm)
C6  = (114 * mm,  162 * mm)
C7  = ( 81 * mm,  114 * mm)
C8  = ( 57 * mm,   81 * mm)
C9  = ( 40 * mm,   57 * mm)
C10 = ( 28 * mm,   40 * mm)

Carta = (216 * mm, 279 * mm)
Oficio = (216 * mm, 330 * mm)

_4A0 = (1682 * mm, 2378 * mm)
_2A0 = (1189 * mm, 1682 * mm)

Letter = (8.5 * inch, 11 * inch)
Legal = (8.5 * inch, 14 * inch)
Junior_Legal = (8.0 * inch, 5.0 * inch)
Ledger = (17 * inch, 11 * inch)
Tabloid = (11 * inch, 17 * inch)

ANSI_A = (8.5 * inch, 11 * inch)
ANSI_B = ( 17 * inch, 11 * inch)
ANSI_C = ( 17 * inch, 22 * inch)
ANSI_D = ( 22 * inch, 34 * inch)
ANSI_E = ( 34 * inch, 44 * inch)

Arch_A  = ( 9 * inch, 12 * inch)
Arch_B  = (12 * inch, 18 * inch)
Arch_C  = (18 * inch, 24 * inch)
Arch_D  = (24 * inch, 36 * inch)
Arch_E  = (36 * inch, 48 * inch)
Arch_E1 = (30 * inch, 42 * inch)
Arch_E2 = (26 * inch, 38 * inch)
Arch_E3 = (27 * inch, 39 * inch)

# To do
#Name 	in × in 	mm × mm 	Ratio 	dot x dot
#Organizer J 	2.75 × 5 	70 × 127 	~1.8142 	
#Compact 	4.25 × 6.75 	108 × 171 	1.5833 	
#Organizer L, Statement, Half Letter, Memo, Jepps* 	5.5 × 8.5 	140 × 216 	1.54 	
#Executive, Monarch 	7.25 × 10.5 	184 × 267 	~1.4483 	
#Government-Letter 	8 × 10.5 	203 × 267 	1.3125 	
#Foolscap, Folio[5] 	8.27 × 13 	210 × 330 	1.625 	
#Letter, Organizer M 	8.5 × 11 	216 × 279 	~1.2941 	
#Fanfold 12x8.5, German Std Fanfold 	8.5 × 12 	216 × 304 	1.407 	612 × 864
#Government-Legal, Folio 	8.5 × 13 	216 × 330 	~1.5294 	
#Legal 	8.5 × 14 	216 × 356 	1.6481 	
#Quarto 	9 × 11 	229 × 279 	1.2 	
#US Std Fanfold 	11 × 14.875 	279 × 377 	~1.3513 	792 × 1071
#Ledger, Tabloid, Organizer K, Bible 	11 × 17 	279 × 432 	1.54 	
#Super-B 	13 × 19 	330 × 483 	~1.4615 	
#Post 	15.5 × 19.5 	394 × 489 	~1.2581 	
#Crown 	15 × 20 	381 × 508 	1.3 	
#Large Post 	16.5 × 21 	419 × 533 	1.27 	
#Demy 	17.5 × 22.5 	445 × 572 	~1.2857 	
#Medium 	18 × 23 	457 × 584 	1.27 	
#Broadsheet 	18 × 24 	457 × 610 	1.3 	
#Royal 	20 × 25 	508 × 635 	1.25 	
#Elephant 	23 × 28 	584 × 711 	~1.2174 	
#Double Demy 	22.5 × 35 	572 × 889 	1.5 	
#Quad Demy 	35 × 45 	889 × 1143 	~1.2857 	
#
#Personal Organizers and Other Corporations[10][11]
#Company 	Name 	Paper Size in x in (Various hole sizes)
#Filofax 	M2 	103 x 64 mm with 3 holes
#	Mini 	105 x 67 mm with 5 holes
#	Pocket 	120 x 81 mm with 6 holes
#	Personal 	171 x 95 mm with 6 holes
#	Slimline 	171 x 95 mm with 6 holes
#	A5 	210 x 148 mm with 6 holes
#	Deskfax (B5) 	250 × 176 mm with 9 holes
#	A4 	297 x 210 mm with 4 holes
#
#Franklin Planner 		
#	Micro 	2⅝ x 4¼ (66.675 x 108 mm)
#	Pocket 	3½ x 6 (89 x 152 mm)
#	Compact 	4¼ x 6¾ (108 x 171 mm)
#	Classic 	5½ x 8½ (140 x 216 mm)
#	Monarch 	8½ x 11 (216 x 280 mm)
#*Jeppesen Aeronautical Charts 	Jeppesen Chart 	5½ x 8½ (140 x 216 mm) 7 holes
#
#FAA Aeronautical Charts 	FAA Chart 	5½ x 8½ (140 x 216 mm) 3 holes at top
#Index and business cards Name 	in × in 	mm × mm 	Ratio
#Index card 	3 × 5 	76 × 127 	1.6
#Index card 	4 × 6 	102 × 152 	1.5
#Index card 	5 × 8 	127 × 203 	1.6
#International business card * 	2⅛ × 3.37 	53.98 × 85.6 	1.586
#US business card 	2 × 3.5 	51 × 89 	1.75
#Japanese business card 	~2.165 × ~3.583 	55 × 91 	~1.65
#Hungarian business card 	~1.969 × ~3.543 	50 × 90 	1.8
#
#Photograph sizes Name 	in × in 	mm × mm 	Ratio
#2R 	2.5 × 3.5 	64 × 89 	1.4
#- 	3 × 5 	76 × 127 	1.6
#LD, DSC 	3.5 × 4.67 	89 × 119 	1.3 (4:3)
#3R, L 	3.5 × 5 	89 × 127 	~1.4286
#LW 	3.5 × 5.25 	89 × 133 	1.5 (3:2)
#KGD 	4 × 5.33 	102 × 136 	1.3 (4:3)
#4R, KG 	4 × 6 	102 × 152 	1.5 (3:2)
#2LD, DSCW 	5 × 6.67 	127 × 169 	1.3 (4:3)
#5R, 2L 	5 × 7 	127 × 178 	1.4
#2LW 	5 × 7.5 	127 × 190 	1.5 (3:2)
#6R 	6 × 8 	152 × 203 	1.3 (4:3)
#8R, 6P 	8 × 10 	203 × 254 	1.25
#S8R, 6PW 	8 × 12 	203 × 305 	1.5 (3:2)
#11R 	11 × 14 	279 × 356 	1.27
#A3+, Super B 	13 × 19 	330 × 483 	~1.46154
#Postcard size limitations Dimension 	Minimum (inch) 	Maximum (inch)
#Height 	3.5 	4.25
#Width 	5.0 	6.0
#Thickness 	0.007 	0.016
#
#"Letter pads" are 8.5 by 11 inches (215.9 by 279.4 mm), while the term "legal pad" is often used by laymen to refer to pads of various sizes including those of 8.5 by 14 inches (215.9 by 355.6 mm).
#There are "steno pads" (used by stenographers) of 6 by 9 inches (152.4 by 228.6 mm).
#
#full sheet of "royal" paper was 25 × 20 inches, and "royal octavo" was this size folded three times, so as to make eight sheets, and was thus 10 by 6¼ inches.
#
#United Kingdom:
#Name 	in × in 	mm × mm 	Ratio
#Emperor 	48 × 72 	1219 × 1829 	1.5
#Antiquarian 	31 × 53 	787 × 1346 	1.7097
#Grand eagle 	28.75 × 42 	730 × 1067 	1.4609
#Double elephant 	26.75 × 40 	678 × 1016 	1.4984
#Atlas* 	26 × 34 	660 × 864 	1.3077
#Colombier 	23.5 × 34.5 	597 × 876 	1.4681
#Double demy 	22.5 × 35.5 	572 × 902 	1.5(7)
#Imperial* 	22 × 30 	559 × 762 	1.3636
#Double large post 	21 × 33 	533 × 838 	1.5713
#Elephant* 	23 × 28 	584 × 711 	1.2174
#Princess 	21.5 × 28 	546 × 711 	1.3023
#Cartridge 	21 × 26 	533 × 660 	1.2381
#Royal* 	20 × 25 	508 × 635 	1.25
#Sheet, half post 	19.5 × 23.5 	495 × 597 	1.2051
#Double post 	19 × 30.5 	483 × 762 	1.6052
#Super royal 	19 × 27 	483 × 686 	1.4203
#Medium* 	17.5 × 23 	470 × 584 	1.2425
#Demy* 	17.5 × 22.5 	445 × 572 	1.2857
#Large post 	16.5 × 21 	419 × 533 	1.(27)
#Copy draught 	16 × 20 	406 × 508 	1.25
#Large post 	15.5 × 20 	394 × 508 	1.2903
#Post* 	15.5 × 19.25 	394 × 489 	1.2419
#Crown* 	15 × 20 	381 × 508 	1.(3)
#Pinched post 	14.75 × 18.5 	375 × 470 	1.2533
#Foolscap* 	13.5 × 17 	343 × 432 	1.2593
#Small foolscap 	13.25 × 16.5 	337 × 419 	1.2453
#Brief 	13.5 × 16 	343 × 406 	1.1852
#Pott 	12.5 × 15 	318 × 381 	1.2
#
#*still in use in the United States
#
#United Kingdom
#Name 	in × in
#Quarto 	11 × 9
#Foolscap 	13 × 8
#Imperial 	9 × 7
#Kings 	8 × 6.5
#Dukes 	7 × 5.5
#
#Name 	Abbr. 	Folds 	Leaves 	Pages
#Folio 	fo, f 	1 	2 	4
#Quarto 	4to 	2 	4 	8
#Sexto, sixmo 	6to, 6mo 	3 	6 	12
#Octavo 	8vo 	3 	8 	16
#Duodecimo, twelvemo 	12mo 	4 	12 	24
#Sextodecimo, sixteenmo 	16mo 	4 	16 	32
#
#demitab or demi-tab 5.5 × 8.5 in (140 × 216 mm)
#size 8 × 10.5 in (203 × 267 mm) is common for a demitab
#
#17×11 is short grain paper and 11×17 is long grain paper
#
#PA4-based series Name 	mm × mm 	Ratio
#PA0 	840 × 1120 	3:4
#PA1 	560 × 840 	2:3
#PA2 	420 × 560 	3:4
#PA3 	280 × 420 	2:3
#PA4 	210 × 280 	3:4
#PA5 	140 × 210 	2:3
#PA6 	105 × 140 	3:4
#PA7 	70 × 105 	2:3
#PA8 	52 × 70 	≈3:4
#PA9 	35 × 52 	≈2:3
#PA10 	26 × 35 	≈3:4
#
#Name 	mm × mm 	in × in 	Notes
#DL 	99 × 210 	3.7 × 8.3 	common flyer 1/3 of an A4
#DLE 	110 × 220 	4.3 × 8.7 	common envelope size as it fits an A4 sheet folded to 1/3 height.
#F4 	210 × 330 	8.3 × 13.0 	common in Southeast Asia and Australia. Sometimes called "foolscap" there.
#RA0 	841 × 1189 	33.0125 × 46.75 	
#RA1 	610 × 860 	24.0 × 33.9 	
#RA2 	430 × 610 	16.9 × 24.0 	
#RA3 	305 × 430 	12.0 × 16.9 	
#RA4 	215 × 305 	8.5 × 12.0 	
#SRA0 	900 × 1280 	35.4 × 50.4 	
#SRA1 	640 × 900 	25.2 × 35.4 	
#SRA2 	450 × 640 	17.7 × 25.2 	
#SRA3 	320 × 450 	12.6 × 17.7 	
#SRA4 	225 × 320 	8.9 × 12.6 	
#A3+ 	329 × 483 	13.0 × 19.0 


import cairo
import tempfile
from math import sin, cos, pi

class PDF(object):
    def __init__(self, file_name = None, size = A4):
        if file_name is None:
            fobj = tempfile.NamedTemporaryFile(prefix = 'pole', suffix = '.pdf', delete = False)
        else:
            fobj = open(file_name, 'wb')
        surface = cairo.PDFSurface(fobj, *size)
        self.__file = fobj
        self.__surface = surface
        self.__size = size
        self.__cr = cairo.Context(surface)

    def __getattr__(self, attribute):
        try:
            return self.__cr.__getattribute__(attribute)
        except Exception:
            return object.__getattribute__(self, attribute)

    def cell(self, x, y, w, h, r = 0, fill = False):
        cr = self.__cr
        if r != 0:
            cr.arc(x + r, y + r, r, pi, 3*pi/2)
            cr.rel_line_to(w - 2*r, 0)
            cr.arc(x + w - r, y + r, r, 3*pi/2, 2*pi)
            cr.rel_line_to(0, h - 2*r)
            cr.arc(x + w - r, y + h - r, r, 0, pi/2)
            cr.rel_line_to(-w + 2*r, 0)
            cr.arc(x + r, y + h - r, r, pi/2, pi)
            cr.rel_line_to(0, -h + 2*r)
        else:
            cr.rectangle(x, y, w, h)
        if fill:
            cr.fill()
        cr.stroke()

    def show(self, program = 'evince'):
        import subprocess
        print self.__file.name
        self.__surface.finish()
        self.__file.flush()
        pdf = open(self.__file.name).read().replace('<< /Creator', '<< /Title Teste\n   /Creator')
        f = open(self.__file.name, 'wb')
        f.write(pdf)
        f.flush()
        f.close()
        a = subprocess.Popen([program, self.__file.name])
        print a
        a.wait()
        print a
        print a.returncode

if __name__ == "__main__":
    pdf = PDF()
    print pdf
    pdf.cell(cm, cm, A4[0] - 2*cm, A4[1] - 2*cm, cm)
    pdf.show()
    pdf.show_page()
    pdf.move_to(10,72)
    pdf.select_font_face("Samserif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    pdf.set_font_size(72)
    x_bearing, y_bearing, width, height, x_advance, y_advance = pdf.text_extents('Teste')
    print "x_bearing, y_bearing, width, height, x_advance, y_advance"
    print x_bearing, y_bearing, width, height, x_advance, y_advance
    pdf.show_text('Testes')
    pdf.set_source_rgb(1, 0, 0)
    pdf.set_line_width(0.1)
    pdf.move_to(10,72)
    pdf.rel_line_to(x_bearing, 0)
    pdf.rel_line_to(0, y_bearing)
    pdf.rel_line_to(width, 0)
    pdf.rel_line_to(0, height)
    pdf.rel_line_to(-width, 0)
    pdf.move_to(10,72)
    pdf.rel_line_to(-3, -3)
    pdf.show_text('Testes')
    pdf.stroke()
    
