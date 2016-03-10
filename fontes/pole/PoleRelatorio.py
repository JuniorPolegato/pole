#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PoleUtil
import PolePDF
import base64
import cStringIO

paragrafo = PolePDF.paragrafo
normal_esquerda = PolePDF.normal_esquerda
grande_esquerda = PolePDF.ParagraphStyle('normal', fontSize = 18, leading = 18)

# Conveniência
cf = PoleUtil.convert_and_format
formatar = PoleUtil.formatar
cm = PolePDF.cm
mm = PolePDF.mm

LOGO_PYTHON = 'iVBORw0KGgoAAAANSUhEUgAAAlkAAADLCAYAAABdyYYmAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAK8AAACvABQqw0mAAAABZ0RVh0Q3JlYXRpb24gVGltZQAwNi8wNS8wNE2+5nEAAAAldEVYdFNvZnR3YXJlAE1hY3JvbWVkaWEgRmlyZXdvcmtzIE1YIDIwMDSHdqzPAAAgAElEQVR4nO3df4wb14Ef8K8U2TJHPyyZG9tra9SzHXESXNKQcpKeKdTORVSCwtm93B/XVVLgEPbiBpCApEFXV6NANo1yRdXzormiWF1aO6GAtlfvFW1SblXk4t00daJxfjQic3GQzMq/ItpexdnRr5VIWbI1/YM73OFwfrwhZ4Yc7vcD2OQM37x53F0tv/vemzcbDMMwQERERESh2tjvBhARERENI4YsIiIioggwZBERERFFgCGLiIiIKAIMWUREREQRYMgiIiIiigBDFhEREVEEGLKIiIiIIsCQRURERBQBhiwiIiKiCDBkEREREUWAIYuIiIgoAgxZRERERBFgyCIiIiKKAEMWERERUQQYsoiIiIgiwJBFREREFAGGLCIiIqIIMGQRERERRYAhi4iIiCgCDFlEREREEWDIIiIiIooAQxYRERFRBBiyiIiIiCLAkEVEREQUAYYsIiIioggwZBERERFFgCGLiIiIKAIMWUREQ6her0NVVczMzKBWq/W7OUTr0qZ+N4CIiMKh6zoqlQo0TUO1Wm3tP3DgQB9bRbR+MWQRESWYGaxUVWWPFdGAYcgiIkqwUqkETdP63QwicsCQtU6cOXcZSxcaWDy3AsDAmaUVrDSuAwDOXazj9YsNwDAsRxiAsfoIYHRHCnfvkFrbD943AsDA6M4tGN2Zwp7RHdiWuiXGd0RERDTYGLKG0JlzKzj98nmcfuU8zpxbwdLFeltgAtAKVIa5z+h8DZbXli7UsXThamu78tJv18qs1r0tdQveNXo7HrzvnXj4d+9B5p4dkbw/IiKiJGDIGhJnzq3g6R/+GpVXLmDpQgPoCE8uAcslfLke79HbtdK4jsqLv0Xlxd/iqflfIHPPDkzs24NHP/A7vb9BIiKihGHISrjTr1zA17/3Ik6/ct6SlboJWIb/8R4By+n4xdcu4Ct//WM89czz+OI//BD2PnBnV++RiIgoibhOVoL9xbc1HD7x/8QClmHEELAMx+OXLlzFoa99F0995/nu3igREVECMWQl1J996xeY/eFZ+AWc9u1eA5YB74CFzvLG2vZTzzyPr8z+KOhbJSIiSiQOFybQ17/3Ek5WX4dvwGnb9gpYQQKX1/HoDFi2sid/8hIAA1+c+D3Rt0tERJRI7MlKmKWLDTz1vRcRLGAZ0Qcsy3CkX90nf/ISZr//K+H3TERElETsyUqYr3+v2RPkFmJGd9yGiYd+B5nR7di6eROWLjbw9HMv4/RLukN5l4Blfw3wnpMVcEI8DANf/dZP8fDv7sLoHVsDfgWIiIiSgSErYdYmuXeGmD13b8Pxf/whbL1tbVHQPaPb8fB77sLJ0zV85X/8DO4hyKW3CmgPUV1PiO88/qnv/BxfPPiQ4DsnSr56vQ5JkvrdDKLIlMtl3zLj4+Mol8sYGRlBPp93LadpGjRNw759+5BOp8NsZmw4XJggSxcb7WtgWQLW1ts2dQQsq0f3yvjMR/Y4DPFZty3PAwUsA0EDFgCc/PELWDp/xftNEyWcrusol8t4/PHHsbCw0O/mEEVqw4YNbf/Nzc117AOAubk5lEol6LruWtfc3Bzm5uY8yww69mQlyLmL1+A2DPdo7l7XgGWayN+PpxZW73EWaEJ7j/O1HMs3H599voaJh9/j2W6ipKnX61BVlTdtpnVnbGysbbtcLnfsM42MjKBarWL//v0dr+m6PhT/dhiyEmTl2o3VZ50h5uF3+y/0ue22W5AZvR2Lr19cqwfoak5V+7ZTebEesNMvnmPIoqFQr9dRrVZRqVRQrVb73RyigVcoFPDMM884hqz5+Xnk83nMz8/3oWXh4XBhgpw5t9I5xAfYQpK3LZvNXB1HwDK8hxgNYKV+XbjtRINsYWEBpVKJAYtIkCzLkCQJmqZ1vKaqKgqFQh9aFS6GrCTxuE3O4tJloSoqLy8jvIBlOJQXPH617JUGQxYR0XpVKBSgqmrbvmq1ClmWEzvZ3YohK3Gsk9aN1T0GTp5+1ffIk6fPIljAMhzKu0yI9wpYHmtoLb6W3AmNRETUm1wuB1VVUa/XW/tUVfW86jBJGLKSyGEV9zPnLuGrJ3/hesji0iV89X/93Hb8aogKMqfKQGfAgrW8LaAJ95YREdF6k0qlkM/n8dxzzwFoTnjXNI0hi/rE4zY5s8+9hD/9zz/B0oW1vwhWrt3AydNncejJH+DKtRu9TVoXmW9l2LYtrXU6FzMWEdH6tm/fPjzzzDMAhqsXC+DVhQnjHrDMxPLsL5fw7C+XsPW2TRjdIeHM0iV0hh6BgBXKfC3v4w1GLCKidS+TyQBoLj566tQpHD58uM8tCg9DVuIYlrzi3st0pXEDZxqXHF9rPniEoNAClnuYY8AiIiLTgQMHcOLECUiSBFmW+92c0HC4MGFEAlb7nCjba0DnnKrAActwKN9lwAqw/AQREQ2nfD6P5eXloVi2wYo9WQniG7D8Ak5bGafyAYYTuzzecGoHERENpSeffFJofyqVcizrdnxSMGQlide6VANymxyvHjHngMWwRUREw4khK4m6CDh9C1iWtbzc20ZERDR8GLKSpq8BS+T49oBleJa11k1ERDRcGLIS5DMfyeAzH8nEcq5DX1vA6RfegHDAcpx/5VK29cCARUREw4shi5x59WAJLzIq2FtGobDfZHWQL4XWdX0o7ktGyVGr1dpu3WIaGRkZqp9FXdexvLzcsX+Qfx8MM4Ys8uE2wd7htW4CFjNWILVaDbVaDWfPnkWtVoOu69B1//s/ptNpyLIMRVGQy+X68qFSr9dRrVahqio0TUv8VUPriT3AA4P9oW3emkXTtNa/GT+ZTKb1b0RRFEiSFENLu2e+x+XlZWialqjfBevJBsPgtfRxunLtBk6/fB6L5y5j6UKj7RY4RsczpyE6+7ZXj5DPpHXDVtby/IXXL2Kl/qbLuZzqFglYzsf/6N//k7Xdl04A119pr9+pnWZdm98L3HInIP09YOMWDCMzlFSrVce/xLuhKAr279+PXC4XSn1uzGBVqVRQrVbbXoszZM3NzaFcLnuWGR8fx9jYmG9d09PTjqEjTIqiYHJyUqisSHuOHDnSWlXbS71ebwsni4uLvsfIsoxMJoN9+/b1PXSpqur4s9aNfD6PfD4PRVFCaFnvzO9NtVpthaowKIrSeq8UPvZkxeRk5TU8+8vf4NlfWeY5edyHMPRJ63HfJifQ8RbXfw28+QtbwLLVYX1sPL+2vfX3gTs+BWy6s7PehNE0Daqqhhqs7PVrmgZFUTAxMRH6h2OYH3YULa8gLMLsKVpYWICiKBgbG4s9mKiqinK5HFrwMOtUVbVv78kU1++CcrmMYrE4MKFyWDBkRez0K+fxZ9983tJj1Rli1nKEYMBymtM0SLfJCRrQ2th7sASClvm48l3g6g+B9GPA9v1IIk3TMDc3F3lPifV8R48eRbFYDPUv2VKpFFpdFA1d11Eul0P98DY/sPfv34+DBw+GUqeXer2O48ePR/rvxfqexsfHYxtGjPt3ga7rmJ6eju17t14wZEXkyrW38Bff/hVOVl71DDHiAcsl4LTV1153x2t9DVgOxzuNVHcbsMyD374KvPFV4MZvgPSnOusfULVaDbOzs7H9QrUrlUrQNA3FYrEv56f41Ot1zM7OQlXVyM6xsLCAxcVFTE5ORhZKNE3D8ePHI+ndcbKwsIBqtYrDhw9HOiwad7iyi+N7t54wZEXgyrW3cKj0Y5w5d7m3gBXabXIc6nYasgvtNjlBAlaIPVnW48//l+Zcre2Dfx+scrmMubm5ro93moDsdiWVF/NDl0FreM3Pz2Nubi6WYFKr1TA9PR3Jh7Wqqn3pLTV7ew4dOhT6sJqu65idnUWlUgl8rFtbug1qUX7v1huGrJAFC1geISiG+wgGO76zrcIBy6+3rEOPAct8PPdvgc33N/8bQLquY2ZmRujKJ6tcLgdFUVoTjt3Yr+YToaoqRkZGhCaAr1duvRjLy8u+c4LS6TRGRka6Pke3lpeXUS6Xu/rQlSSp61BWq9Vw/Phx4Un8IoIGLFmWW/9mdu3a1RYarFchig6b1ut1TE9PhzrEHjT85nI5ZLNZKIrie3Xg4uIiKpUKVFUN9H00e9f5R1dvGLJC9s//a8USsDpDjGMw6SkgCYSYMAOW321y7Mf7ti2inizz8Y3/AMj/BoPG/EtR9JeeeQVQNpsV/stSkqTWVUOapqFUKglNDC6Xy8hkMpwA62JiYsJxv8gVjPv27etLgBUNJel0unVpvyzLHR/gtVqtNSFc9GdX0zQsLCxg//7e50kGCVi5XA779+/3/DlOp9OtfyP1eh0LCwuYn58Xem+zs7OQZbmnQKzremuo3o8kSSgUCigUCkilUsLnyGQyyGQyGB8fx/z8vO/PqJWqqshms5FfhTzMGLJCNPvDX+P0y+aHWFgBy6O3q+eAFTAECd2HsJsw115NaAELBnD1b4FLzwC3H+g8V58ECVj5fB7j4+M9r2WjKAqmpqYwPT0t1HNWKpUwNTXFoYJ1IpfLtUK8F1mWMTExgfHxcZRKJeGhraeffhrZbLann+NarSYUsCRJ6mo4T5IkjI2NIZ/PCwUfs0dramqqq/elqipmZ2d9fw90G67sUqlU6yrJmZkZ4ZA8OzvLkNWDjf1uwLBYutjAU999YXXLJZgYsAWCqAOW4VBe8HiHthrm++g4V0gBq605tsDkF7AMa3lbm85/y/1cfSAyLJBOpzE1NYVisRjaYoGSJGFyclLoL29d13uaJ0bJkM/ncezYMRw6dMg3YFmlUikcOnQo0HBZkB4Uu3q9jpmZGd9ysixjamqqp17YdDqNyclJofdmtqub4VSR3kDzj6OxsbGeApZVJpMJNNfKHFKl7jBkheTr/+cFXLl2A20hwh6wuu1B8gwxgj1QXue3tNXtXOY7cT6XW9vgUt4W0KzsASlwT5atTQaAay8A117EoBD5hVwsFiO5gkmSJBw+fFjoF+z8/Hyo6w7R4FAUBUeOHOk5xBeLReFejqBzgqxOnDjh+7No/hER1h8lonOuzDXCohBGL7YTWZYDzbXienfdY8gKwdLFBk5WXoNTwOktYIXQS9QxydwW0ATCXPcBy/Bom9H20KajJ8sanqyPtv0dr1mOP/9NhxOtT+l0WnheUC+9DzR4JElCsVjE5OSk0ArwIorFonCvyHPPPRe4fk3ThIYlDx06FPrwtuhCveVyOfAFLP0WZK5V0t7bIGHICsGzvwy6iru5TzSECAYsw77tULdTz5Bj3SIBy+goLxwmW4faUpZTQLK/17YytnZ09GStbl8+BVpTKBSE/kJWVZW9WUMil8vh2LFjod8+JZVKuV4MYNfN8gQi87D8Jrh3S5Ik4fc2Ozsb+vmjJvreGLK6x5AVgpOVV5tPhAKWsfafVwhpPbiEGIEhPu+6RQKWQ3gJcHzbc8e2GsjscricvSNg+fRS2c/h1Mv19pWBGjIcBIWC2Bpi8/PzEbeEonbw4EEcOnQotHk9dvl8XqgXKeiHtUjIlyQJ4+PjgeoNwryy14+5FESSmDeL9hPXgq/DiCGrR1eu3VhdsmEtEAS+D6E9hADw7CUKZUK8ue0VsOBzvNf53eu2NBBbpc1o8/YVdAYsazusAcuhTq95W+zNaiPaoxHlyuAUjzhu3Cw6UTxIz6jIcPVDDz0U+VWwoiEuiReL8MrBaDFk9ej0K+dtAQuCAcslhADtIaaLIT7nuty2O48Xv02OQ9vatr2+Dk333LGtbRvXX3YIWLYeq24CFgBc4eRNK0mShK4oMxc1JfIiOlwnGrI0TRMqe+BA9MuzpNNpoX8rom0eJFwPL1oMWT06s3R59ZngbXK8QohZxhTZFYcCAcs+HOl3fNC5ZKv2Zu5d23ANWD6P1vN7PV79Wcf51zvRX7DdzKWh9SXIEhAiRHpQnRZMjYpoz2/ShtejGkKmJoasHp1++TzWApYl4LiFAK8QIhSwHHqQnEKMb0DqbGugVdxDCFgA8KA1ZDWe7zwmrIBl1tsw1zIjQDxkJW2uCfVHmIFHpPc0rCskReRyOaFhyaT9W4ljKHk9Y8jq0U9fXrYErFWuQ3wiISRgD1LXAau9reHeJkcsYD3y/vtxt3W4cGWh/WsXdsAywN4sG9FfsLquJ24YhOIncl9GEYuLi0KTreOeTyQS6mq1Gv+tUAtDVg+WLjaaT4R7oOATQkRCjFP5IAGts62et8lxuSrQt26fgAUABz/y/rWNt96wXP0XUcBiT5Yj0d4AXsZNcRHtDYq7F4Y9vxQUQ1YPzixdRvCAhbV9gQNWDwGtLTA1nzdrczqXW90i79WlvM3Bj7wfe/fcs7bj/F+t1SPSk9VNwDIAXF9ybdN6Jdr7wJBFcRG9YXLc99YUDXX8t0ImhqweLC5dWn0WsAfJM8QI9kAFDVi23i7DrWzroZuA5RTQOmV2jeCxRz+0tqPxc+Dygnsw6rYny+m4FV4lZyc6j4Z/nVNcRELKrl27YmhJO9GeLIYsMjFk9aA5XCjaA2Vu99hLZH/Nfn77VYEO5+o+YImESdt7scnsGsFffuEPsTV1a3PHzavA8lPtAakVjGxfL+v+bgKW+fj2Fdf2rUeivQFckJDiIvKzFncvVhAMWWRiyOrB0oWrtoAVNIT4BCzDvu1Qd+t46+tOdYsELMOjbT5hsnWoe8Dam7m3PWABwPKTa3OxnN6rU8BqNcPWbqGgZnBelg2HQGiQiP6c9euqOJE5jPyDhEyb+t2AJLvSuAHhENJ6cAkxoczX8j6+91XcXc7vE662pTbjsY9/EBO///72F974C+DSfHv91qDXEbQc2toWouztcjmeiAZWo9HodxNCUavVuDwCMWT1on1OFtaeA8FCTGgByz3MhXObHOe63QJWZtcIPv7Qu/Ho772nvfcKiCBg+dVjeVypAFvDXThxveAHB5GYYQmL1BuGrJ75hBDAIRi4vBZSwNr7rruQufcObE3d4pB/bDsce3eMtgfnEGU47jZXcM/sGukMVkBzDtbSvwLqfwt0BCSX8Ck878p8TeA46go/OIiIxDFk9cKvB6mtjFP5AD1Inscb2Puuu/HoBx/AI++TsfU2h3AzCC7+z+ZSDW9fRfgBK2A91DLIE4iJiJKMIatngsNoYU6It2zvfdddeOxj70fugbt6extRuXkVWJkHLpaBG7/pLRgFCVqex4f4/oYAh/+IiKLBkNUTkYAkMuTndbxTeQPbUrfiMx/7u5h4+D3uzXvrLGBcdQkVhuem40GGz+vm7rd+A9x4A6j/CHjzRf9gFXbAYk9WILxqkIgoGgxZvep5TpVTee/jt6VuxfHDH8Wee3ba2lIHrn0fePP7wI2z6DqAhBZkBI7vS8Bi0LLi5eZE4WMPMQEMWT3J3L3d4QrDIAEreEBzDFhGHah/E7j2g+bwnL2+qAKS1/Fh1xN2cCOigSR6B4JB/+MglUr1uwk0ABiyerA1dcvqM7eAZPlA9wpYHT0sAQLWW2eBlX8HvL08eAFpUAMWc1bXRD8Aibol+jPWr2FukfPyYhIyccX3HozulBB5wDKMVpkvfjLfHrCunwYu/evBDFiGYCCKPWAZwPa9oDVBegQYsigOIj9n/VpOROS8HCokE0NWD0Z3SsECljVU2F/rON5oK/vI+3bh4fda/uG+dRZYeRIw6tH0HIURkGIJfIZLfYZHvSALTnynQTMyMuJbph8/t7quC5VjyCITQ1YPMqM7EChgtZW1BSzDKSi0KsIXPvEhy2a92YMVVcAKqz63IGTd73i8IdgOa2iyHw/3erfnQGtEe7IURYm4JURNoj9rcQet5eVloXIMWWRiyOpBc7gQcAwengELa8/N8q7bBh794AO4e+eWtRNf/asIApZbsAkakGzttwche0BybIdlv2s7bMd0HO9QxgCweRTUTvSDikOFFJdBvWm5pmlC5fgHCZkYsnqwZ/T29iAAtIeHngNW8+HgI5a1sN5ebi7T0BFk3Hp6fAKVPdh49RQJBSSHoOkVfvzKOLbD4Wvt+DVw2M/5WB1EP6h2794dcUuImrJZsXuLioaesIgMF6bTaf5BQi0MWT3ae/87ESxgOQQfj4A1escW7LnnjrVqr/2NS0ixnUO0p8jeLq9eINfw41TGHu6cjnFph7V9nuHQWsYjZFq/D1IGtKZWqwlPIM5kwv3acS4Yecnl/If14w5ZIudjLxZZMWT1KHPP7c0ntiE+94AFh/Ju2wYeeZ+t96Dx/bbX254H7imytcs1yNjq9Qpq1sewAlKY88d2PgxaI/ohJUlS6PNMeLNp8iLSm6XremxhXdd1oZ6sQqEQQ2soKRiyerT3gTsdApLledcBq2nUOherdZscpwBinku0p8gpYLk9OgUsr4AkWq/LcUHr8Tve/DptHuWcLBvRkCU6fBOE6CRiWp9EerIA4NSpUxG3pKlSqfiWSafTnPRObRiyetS8whAQC1i2sAJ4BiwYBjL3WoYK3172CCBBe4osj35BKEggChKwggSkXtsFADsfAa3RdR3ValWo7L59+wLVLfJBE/dQDyVLKpVCPp/3LaeqagytETvPgQMHYmgJJQlDVo/u3inZhgy9AhbWnrfKW16zBSxrbQCAt36NyAJIPwJWWO0TDWrvHAOtEe0BSKfTgedjiax4LRrwaP0aHx/3LdNoNCIPWpqm+Q5LSpIkFAppfWHICkH7kCHaP/ix+ugXsGy9XYa1LNBZNuwA4lVPPwNWWO3bPAps2QNqqtfrmJ+fFyrbzV/nIldX1ev12HohBgWHSINJp9NCw4blcjnSexmWy2XfMoVCgfcrpA4MWSF49MH71jbsw3/2gGWdjO7S2+UcsNB5TFgBxOt40aAWVcAKq32jn7R/Ide1UqkkNPG827/ORa+wivrDMU4i71l0xXBaMzEx4VtG13XhPxqC0jQNi4uLnmXS6TTGxthTTp0YskKw554dzQnqrgHLQCtgtQgErLby1qpDDiBxDTlG1TMmUs+dyfoFqKpqZOFDVVXhobqJiYmu/joXnbSs6zpmZ2cD1x+EpmlCk5Z7JfJ14rIVwaXTaaFhw7m5udC/vvV6HTMzM77lDh48GOp5aXgwZIXkMx997+ozh4Bjbre4BSzDpby16ggCiF89YQS1fk6ef+fHgXdsRZKoqorHH3889OG0Wq2GUqkkVFaW5a7nmIhOWgaa71W0TUHouo5SqYTp6elYwo0sy75z0er1OueidWFsbEzoYoonnngitD9O6vU6pqenfXt8C4VCJFff0nBgyArJox+4D6N3rP6C9byC0Ctgwfn4tRfCDyCiASmMQOTZDoevTWufU32GeL27P4skajQaKJVKoYUtVVVx9OhR4fLFYrGn84n0PphUVcX09HQow2n1eh3lchlHjx6Nfc6XyIdtVMNaw65YLPqG2EajEcrPUb1eR6lU8g3nsiwH+jmn9YchK0RTEw/5BCy0hwihgOUQtKzlegogovWZ5Q2XegSCkGEr3xGw4NAeA2tfBpf9XkHNMJrDhAlfG8vskfnc5z6Hcrkc+ANE13U88cQTgXqLisViz+v9iA7zmDRNw9GjR7t6j+bxpVIJn//85zE3N9eXuV4iS11omoa5ubkYWjNcZFkWCv61Wg1f/vKXu14iRNM0TE9P+/Y4SpKEYrHIye7kaVO/GzBMcg/ciUc/eD9O/uTF5o5eA5bTkKF1v2uwaRV0DzL2/V71mNs9He/WDof36hjmHPY71mPZ3rQNuG8Sw6LRaGBubg5zc3OQZRmZTAaKomD37t1tV/PV63XUajXUajWoqhp4qCyfz4d2KfrY2Bg0TRP+wKvX6633mM1moSgKZFl2HIrTNA26rkPTNFSr1YGYQJ/JZJDL5XzngJXLZdRqNXz6058WWu6CmrLZLIrFou8fDGaPViaTwfj4uNBFCZVKRXi+oiRJmJyc5MKj5IshK2Rf+MQHcOb181h89fzqHoGAZZ+v1bHP+rJPEBIKILb9IvW2lbHXGyAgdZwr4PGe78/2+K5/CWxK1lwsUWaIWlhYCLXefD7f8zCh3eHDh/HEE08EDnvVajWR85eKxSI0TfMNfZVKBZVKBfl8HtlstiMskzPzDwCRntnFxUVMT0+3VmJ3CkXmGliit3liwKIgGLJCtvW2W3D80EdxaOY7WHxtdcjDIcyIBSxb0OopYLns96rH/tjRBqf31mXACnt4c/STQPrDSCpFUWJfET2KgAU0J8EfOXIEMzMz62KV91QqhcnJSUxPTwv1rqmq2jZ3LJ1OI5vN8oo1D/l8HpIkoVQqCX2NzfsO9hrazSFLBiwSxTlZEdh62y04fvgADj78nmABy4BD2LBxnM/kFEBiDFiGQzuc2hdXwLrvnwH3J3uYcHx8HFNTU8LrTfXq4MGDkQQskxk84r55rrnO17Fjx2I9ryzLmJyc7KpnStd1vPrqqxG0arhks1lMTU3FFngKhUKs56PhwJ6siGy97Vb80098EI+8bzee/HYVp88swYxYzQdbb5U1RNhDRZseA0iQQBOk3kGo5/YHAfmzzcchYH5QLy4uolwuR9ILpCgKJiYmYvvgmJiYQC6Xwze+8Y1IF+bM5XLIZrPI5XJ9m5gsyzK+9KUv4emnn153K9vHJZ1OY2pqCqqqYnZ2NpJ5eXH/G6HhwpAVsdwDd+H44Y/h3Pkr+L8/P4ufvrCElfp1nHlNx0rjzWahMAJW2EEmquAW5vHb964+Pgjc8WFgS7D76yVFJpPB5OQkarUa5ufnQ5nkrShKqBPcg8hkMjh27BhUVe36SkK7dDoNRVGgKErXwSqK+VCpVArFYhHj4+Mol8sDM0F/2OTz+dYFB/Pz86Gsi5bP57Fv377A9+0kstpgGG4zrGngXP5vwOW/jidg7f5zQHpftO9nnZqenvbtlTpy5IjnL/dqtdq6ak/0A0WW5VYPzyD9VW69ClKkt05RFEiS1JrILMuyUEB67LHHPF/3+5qHoV7rvpUAAArWSURBVNFotL5nmqZheXnZMWQqioLJSbEhb5FJ27Isx9KjNyhtMedfaZqGs2fPCgV5RVFa90pUFCXyNg7K1wqA722DADBsdok9WUkT55AcDaxsNtu28KX5S7JWq7V6StLpNEZGRpBKpQYqVNnJstxxfzr7L/1ef8GLfIjEIZVKtb53Yd3rbpC+t4PSlnQ6jf3792P//v2tfW4/A+l0ui9XdQ7K1wpggIoSQ1bixBWwGLSSxPwlOSy/LIflfdDg4M8U9QNDVqLEMCfLLPebrwEbpLXybfU4tKdtG871wna8Wd+7/W/AShQ1rtxNRGFjyEqSOIcKGy/0Xk+gdhH11yAN3xDRcGDISprQgpa1VynMoGart3WctZfLtp+IiGgIMWQlThgByeV4h4VTXQOSYz1dBCxmLIrB8vKy5+vsxSKiKDBkJUoYAckevoIe79YOh+E/x1XgHfYTRczvEn7epJmIosCQlSQdvUGr/wsrYAUJSB3ncnhkwKIBwZ4sIuoHhqykcQ1YHkEmyLCi6/GW/V7Hd7t6O1GE/HqyRkZGYmoJEa0nDFmJ4hdo4BKQBANWL7fH2ZYD3vlHwI6/39z35hKg/2/gta/7H08UMb+V5NmTRURRYMhKmkG4D6G9fPofAH/nX7S3c/MocM+fNMPXLw/710MUkWq16luGC1USURQ29rsBFEBbb9XqjrgDlmErf+vdwK7Pubd5217g3j9hwKK+qVQqnq8rihJTS4hovWHISpp+Byx7fXf+EfCOrd5tvnuisx7z+FtHxd43URfq9bpvT1Yul4upNUS03jBkJcnGLc1Ho48By96Tldrj3+53bGv2aDm16zaGLIrOiRMnWjfMdmO90TYRUZg4JytJbr2v+x6nsAJW10N9LvX49YIRdUlVVd+hwnw+j3Q6HVOLiGi9YU9WkqTe23wU7cmKOmAZBlBf9G/3WyvApdPO9Wz/gOCbJxKnqipKpZJvufHx8RhaQ0TrFUNW0mzbv/okpJ4sz3oM//rOzfq3eenpznrN49MfFnjTROLK5bJwwGIvFhFFicOFSbPjD4BLz6xuWMKKY0Ayi3UbsOAQsIzWJgwDuH4OeOkrwP1fdG7v1UXg1f/o3K47x5pLPRCFQNM0zM7Oolar+ZZVFAVjY2MxtIqI1jOGrKTZfB+w8w+AC9/qImDZAhJs5TsClr0eh+MNA1g+Cbz5OnD3QWDnI839by4Bb8wBrz7pXO+mbcDuz/b0pSACmuFqbm7Od8FRkyzLOHz4cMStIiJiyEqm9D8Crv4MePOl3gJSVwHLXs/q9uXTzf/c6rE/3j/JXizqmqZpqFQqqFarvrfMsZJlGUeOHEEqlYqwdURETQxZSbRxC7D7z4Gzfwpce7G3gGQt3/PaWS7tsD9mvtwcKiQSoGkadF3H2bNnUavVsLgocLGFg3w+j4MHDzJgEVFsGLKSygxar08DK2qAgISIApbA46ZtzR4sBixyYfZQ1Wo16LoeqJfKjSRJKBaLXA+LiGLHkJVkG7cAu74EnP8m8Nv/1FwqAQg/IIURsG7/QDNgbeE94shdo9HAwsJCaPUVCgWMj4+z94qI+oIhaxjc8YfA7R8Fzh0HLvxNc19YAanXoLZ5tDnBnb1XJCCM+whKkoR8Po9CocAlGoiorxiyhsU7tgD3HgHu/ONm0Fr+78DbK9H3ZLnVc/uDwOinuA6Wg0KhAEmSfFcjX49SqRRkWRZahsFOlmUUCgXkcjn2XBHRQGDIGja33NUMWnf+MXD5FHDpB83/nAIXEG7Auv1BYOeHm8GKVw66ymazyGazaDQaUFUVp06d6ipUDCtFUYS+HpIkQVEUKIqCbDbLXisiGjgbDCPwTegoiRovAlcqwEoVaCwCb55DT0HrHdsAaQ+w/cFmuNq+N653MpR0XW8FLl3XceTIEWQy63P+WrVaxczMTNu+dDqNkZERyLKMkZERZDIZyLLcpxYSEYlhyFqv3r4KNM40Fw29vtQMTyunW7nLcikikMoAm7auBavNo+ypilCtVoMkSeu2Z6bRaKBWq7WGDomIkoohi4iIiCgCvEE0ERERUQQYsoiIiIgiwKsL14PVEeG4x4U3AMCGDTGflYiIaDAwZCWdYYiFp5iD1gbBczGIERHRsGLISgqvMCUQtOK+vsHAaoDysAGAsWGDZakI2+sMX0RElGAMWQPKNRS5BCq38l7hKszg5RSImktqGa6vu9bVPKCjfez1IiKiJOESDoPCKTwJBiqnb6HoPq/9IrzCk9Nr9n0d282dvvv8zk1ERNRvDFn9JBisvEKVX+Bq2/YZcgTE52z59Sp5hSnfoGUt63Aex30MXERENGAYsvqg40vuE6xEQ1brub0+27ZX3d3oOkAFfd7c4brtto+IiKgfGLJi5BuuBMKQb6iyPHc6xqu+bomErCCBKmj4ctxu7hR9C0RERKFjyIpDD0OA9jDkF7IMw3Cs2+18YYasIAGr29c8nzd3OLaBiIgobgxZUfPprXLqebI+FwlcbmX9tu3HOG27Ee2Bsu9z27YGpCBBzP5cZJuIiCgODFkRE52IHiRM2feJhqsgocz+utuVgm4BSDRc2bf9Hv32AezRIiKiwcB1sqLkMAerbdPxEPf1sexl/AKVSNjy2ufGDEWGYbTCy8aNGzvOZy1nHmc9lzX4tOoyjNYaWRscHu1fq9a+1eOA1YVQLdtERET9wJAVoY55WG7lBCamWye2u9XhtQ6WSMC6efOmaxkzMNlDkxl0bt68iY0b3e837hSsrK9tsAYk11rc+R7H0EVERDFjyIqQ/f59bvfzswYX+z77I1xuQ2PvJXJ7zd4rZN1n743yGyK0vm4PWE7zotyG7DqG+rrQcZz9XAxYREQUM4asKNkDkW3bKXQ5BS57eaegZB5rblt7nZyG7qznM928eVN47pLbfCy314TnXAnMyXI6JzyCGuMVERH1Aye+R81+NSGCTX63Pu+YsG64L90gcjVht1cYii6tEORqQ5GlHLiMAxERJQlDVkz8goxowHLc5xDUgoSpXn4E/JZS8NsnEq5cyzU31vb7bBMREcWJIStO9l4tn16uboKXSFm/Y4LwClnWfa7BSHCJBq9zsfeKiIgGEUNWP/gNIfpsB33ezbYoz56s5k7HbZGhv6D1O5UhIiLqF4asPuv48jsEMPu+bgOZ1z77+Tz5BBmvoGTfDlIWcAlWAm0iIiKKG0PWAHH8VgiELrdjgwasID8Kfj1GvlcDuuxzLNN8wXcfERHRIGHIGlRO4cprP9xDkt+3OKyJ70HKuIUkr/DEoUAiIkoShqwk8QhYnq8FKRMSv56m1itugcrneCIiokHHkDUMRMOTeaVhhE3xC08d5RmkiIhoSHHF92GwYYPwqubd3hswiKBBi4iIaBgxZK0nAcIYERER9WajfxEiIiIiCoohi4iIiCgCDFlEREREEWDIIiIiIooAQxYRERFRBBiyiIiIiCLAkEVEREQUAYYsIiIioggwZBERERFFgCGLiIiIKAIMWUREREQRYMgiIiIiigBDFhEREVEEGLKIiIiIIsCQRURERBQBhiwiIiKiCDBkEREREUWAIYuIiIgoAgxZRERERBFgyCIiIiKKAEMWERERUQQYsoiIiIgiwJBFREREFAGGLCIiIqIIMGQRERERRYAhi4iIiCgCDFlEREREEWDIIiIiIooAQxYRERFRBBiyiIiIiCLw/wHFhXehSRmsyQAAAABJRU5ErkJggg=='

CABECALHO = ("\n"
              "<b>Pole - Python utilities by Junior Polegato</b>\n"
              "This module combines functions for development on a day-to-day\n"
              "Facilitate the use of GTK + for GUI and ReportLab for PDF\n"
              "Send NFe and enjoy its features, including XML")
LOGO = None

# Estilo pradão da tabela
_ESTILO_TABELA = [('GRID', (0,0), (-1,-1),0.5, PolePDF.colors.black),
                  ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                  ('TOPPADDING', (0,0), (-1,-1), 0),
                  ('RIGHTPADDING', (0,0), (-1,-1), 1*PolePDF.mm),
                  ('LEFTPADDING', (0,0), (-1,-1), 1*PolePDF.mm),
                  ('FONTSIZE', (0,0), (-1,-1), PolePDF.normal_centro.fontSize),
                  ('LEADING', (0,0), (-1,-1), PolePDF.normal_centro.leading),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 1)]

def gerar_pdf(paisagem, data_inicial, data_final, titulo_relatorio,
              cabecalho_colunas, sql, dados, conexao, pdf = None, finalizar = True,
              sumario = None, folha = PolePDF.A4, logo = None, cabecalho_logo = None):
    # Acertando os cabeçalhos das colunas
    cabecalhos = []
    cabecalhos_excluidos = []
    casas_default = PoleUtil.locale.localeconv()['frac_digits']
    for (n, registro) in enumerate(cabecalho_colunas):
        registro = list(registro)

        if registro[1] == 0:
            cabecalhos_excluidos.append(n)
            continue

        if len(registro) < 4:
            registro += [casas_default, '']
        else:
            try:
                registro[3] = int(registro[3])
                if len(registro) == 4:
                    registro.append('')
            except Exception:
                if len(registro) == 4:
                    registro.append(registro[3])
                    registro[3] = casas_default
                try:
                    x = registro[3]
                    registro[3] = int(registro[4])
                    registro[4] = x
                except Exception:
                    registro[3] = casas_default
        cabecalhos.append(registro[:5])
    cabecalhos, larguras, tipos, casas, totalizacao = zip(*cabecalhos)
    # Se não passado um logo, usa o logo do Python
    if not logo and LOGO:
        logo = LOGO
    else:
        logo = cStringIO.StringIO()
        logo.write(base64.b64decode(LOGO_PYTHON))
        logo.seek(0)
    # Se não passado um cabeçalho para ir junto ao logo, usa o do Pole
    if not cabecalho_logo:
        cabecalho_logo = CABECALHO
    # Transformando as larguras de centímentros para pontos no PDF
    larguras = [l * cm for l in larguras]
    # Tipos do Python para tipos do Pole
    novos_tipos = []
    for tipo, _casas in zip(tipos, casas):
        if tipo in ('int', 'long'):
            tipo = 'Inteiro'
        elif tipo == 'float':
            tipo = 'Quebrado %i' % _casas
        elif tipo in ('str', 'unicode'):
            tipo = 'Livre'
        elif tipo == 'bool':
            tipo = 'Sim ou Não'
        elif tipo == 'datetime':
            tipo = 'Data e Hora'
        novos_tipos.append(tipo)
    tipos = novos_tipos
    # Estilo das colunas
    estilos = []
    for tipo in tipos:
        estilo = PolePDF.ParagraphStyle('personalidado', normal_esquerda)
        estilo.alignment = (PolePDF.TA_RIGHT if PoleUtil.tipos[tipo][-1] > 75 else
                            PolePDF.TA_LEFT if PoleUtil.tipos[tipo][-1] < 25 else
                            PolePDF.TA_CENTER)
        estilos.append(estilo)
    dados_tabela = None
    # Tenta carregar dados executando via conexão e instrução SQL, qualquer erro usa os dados padrões passados
    try:
        cursor = conexao.cursor()
        cursor.execute(sql)
        registros = cursor.fetchall()
        cursor.close()
    except Exception:
        if not dados:
            registros = []
        elif isinstance(dados[0][0], (list, tuple)):
            registros, dados_tabela = zip(*dados)
        else:
            registros = dados
    # Imagem do logo
    I = PolePDF.Image(logo)
    I.drawWidth = 13 * mm * I.drawWidth / I.drawHeight
    I.drawHeight = 13 * mm
    # Dimensões
    margens = 2 * cm
    largura_folha = folha[0] - margens
    altura_folha = folha[1] - margens
    if not paisagem:
        paisagem = sum(larguras) > largura_folha
    if paisagem:
        largura_folha = folha[1] - margens
        altura_folha = folha[0] - margens
    # Se tiver um pdf, cria uma nova página, senão cria um pdf
    if pdf:
        pdf.nova_pagina()
    else:
        pdf = PolePDF.PDF(paisagem = paisagem,
                          nome_do_arquivo = "/tmp/" + titulo_relatorio.replace('/','-') + ".pdf",
                          titulo = titulo_relatorio + " - " + data_inicial + " à "+data_final)
    # Logo do relatório apenas na primeira página
    altura_disponivel = altura_folha
    altura_disponivel -= pdf.celula(I.drawWidth, 0.5 * cm, None, [I], borda = False)[3]
    pdf.celula(10 * cm , I.drawHeight, None, [PolePDF.paragrafo(cabecalho_logo, PolePDF.pequena_centro)], borda = False)
    pdf.celula(largura_folha - 10 * cm - I.drawWidth, I.drawHeight, '', '', borda = False)
    # Pula 0,5 cm
    altura_disponivel -= pdf.celula(largura_folha, 0.5 * cm, '', '', borda = False)[3]
    # Título do relatório apenas na primeira página
    altura_disponivel -= pdf.celula(largura_folha, 1, None,
                                    [PolePDF.paragrafo(titulo_relatorio, grande_esquerda)],
                                    borda = False)[3]
    altura_disponivel -= pdf.celula(largura_folha, 1, None,
                                    [PolePDF.paragrafo(data_inicial + " à " + data_final, normal_esquerda)],
                                    borda = False)[3]
    # Pula 0,5 cm
    altura_disponivel -= pdf.celula(largura_folha, 0.5 * cm, '', '', borda = False)[3]
    # Altura do cabeçalho das colunas do relatório
    altura_cabecalho = 0
    for largura, cabecalho in zip(larguras, cabecalhos):
        altura_cabecalho = max(altura_cabecalho,
                               pdf.altura(largura, 1, None,
                                          [PolePDF.paragrafo(cabecalho, PolePDF.normal_centro)]))
    altura_disponivel -= altura_cabecalho

    # Transforma em parágrafo cada valor de cada campo, utilizando caracter adequado para booleano
    if dados_tabela:
        # Caracteres para bool: ✔⊠☑✅✓❌❎⨯☒⬚❏⬜'
        dados_tabela = [[paragrafo(('✔' if campo else '❏') if type(campo) == bool else campo, estilo)
                                 for campo, estilo in zip(remove_columns(linha, cabecalhos_excluidos), estilos)]
                                 for linha in dados_tabela]
    else:
        dados_tabela = []
        for registro in registros:

            remove_columns(registro, cabecalhos_excluidos)

            linha = []
            for campo, tipo, estilo in zip(registro, tipos, estilos):
                if type(campo) == bool:
                    conteudo = '✔' if campo else '❏'
                else:
                    try:
                        conteudo = formatar(campo, tipo)
                    except ValueError:
                        conteudo = '' if campo is None else str(campo)

                linha.append(paragrafo(conteudo, estilo))
            dados_tabela.append(linha)
    # Totalização, com exceção de percentual
    totalizado = []
    for n, t in enumerate(totalizacao):
        t = t.lower()
        if t == 'len':
            totalizado.append(formatar(len(registros), 'Inteiro'))
        elif t == 'set':
            totalizado.append(formatar(len(set(zip(*registros)[n])), 'Inteiro'))
        elif t == 'sum':
            totalizado.append(formatar(sum(zip(*registros)[n]), tipos[n]))
        else:
            totalizado.append('')
    # Totalização de percentual
    for n, t in enumerate(totalizacao):
        if t.lower()[:4] in ('perc', 'porc'):
            t, a, b = t.rsplit(' ', 2)
            a = cf(totalizado[int(a)], float)[0]
            b = cf(totalizado[int(b)], float)[0]
            if t.lower()[:4] == 'perc':
                t = 'Porcentagem %i' % PoleUtil.locale.localeconv()['frac_digits']
            totalizado[n] = formatar((a / b) * 100 - 100, t)
    if sum(map(lambda x: x != '', totalizado)):
        # Linha separadora com "Totais" na primeira coluna
        dados_tabela.append([PolePDF.paragrafo("Totais", PolePDF.normal_esquerda)] + [''] * (len(tipos) - 1))
        # Inclusão do totalizado no final dos dados
        dados_tabela.append([paragrafo(t, e) for t, e in zip(totalizado, estilos)])
    # Separação dos dados de cada página
    tabelas = []
    while len(dados_tabela):
        if tabelas:
            altura_disponivel = altura_folha - altura_cabecalho
        t, i, alt_ult_tab = pdf.tabela(sum(larguras), altura_disponivel, dados_tabela, larguras, style=_ESTILO_TABELA)
        tabelas.append((t, alt_ult_tab))
        dados_tabela = dados_tabela[i:]
    # Calcular altura do sumário
    if sumario:
        altura_linha_sumario = 0
        altura_sumario = 1 * cm
        lagura_sumario = 0
        ult_alterada = 0
        for n, celula in enumerate(sumario):
            lagura_sumario += celula[0]
            if lagura_sumario > largura_folha:
                altura_sumario += altura_linha_sumario
                for cel in sumario[ult_alterada:n]:
                    cel[1] = altura_linha_sumario
                ult_alterada = n
                altura_linha_sumario = 0
                lagura_sumario = celula[0]
            altura_linha_sumario = max(altura_linha_sumario, pdf.altura(*celula))
        altura_sumario += altura_linha_sumario
        for cel in sumario[n:]:
            cel[1] = altura_linha_sumario
        # Se o sumário não couber na página que tem a última tabela, soma outra página
        nova_pagina_sumario = (altura_disponivel - alt_ult_tab - altura_sumario) < 0
    else:
        nova_pagina_sumario = False
    # Total de páginas
    paginas = len(tabelas) + nova_pagina_sumario
    str_pagina = "Página: %%s de %s" % cf(paginas, int)[1]
    str_agora = cf(PoleUtil.datetime.datetime.now(), PoleUtil.datetime.datetime)[1]
    # Renderização das tabelas
    for pagina, (tabela, alt_tab) in enumerate(tabelas):
        # Número da página
        pagina += 1
        pdf.celula(largura_folha, 1, None,
                   [PolePDF.paragrafo(str_pagina % cf(pagina, int)[1], PolePDF.pequena_direita)],
                   borda = False, posicao = (1 * cm, 0.55 * cm))
        pdf.celula(largura_folha, 1, None,
                   [PolePDF.paragrafo(str_agora, PolePDF.pequena_direita)],
                   borda = False, posicao = (1 * cm, 0.73 * cm))
        # Cabeçalho das colunas
        for largura, cabecalho, estilo in zip(larguras, cabecalhos, estilos):
            pdf.celula(largura, altura_cabecalho, None, [PolePDF.paragrafo(cabecalho, estilo)])
        # Tabela
        pdf.celula(sum(larguras), alt_tab, None, [tabela], borda = True, espacamento=0)
        # Nova página
        if pagina < paginas:
            pdf.nova_pagina()
    # Renderização do sumário
    if sumario is not None:
        if nova_pagina_sumario:
            # Número da página
            pagina += 1
            pdf.celula(largura_folha, 1, None,
                       [PolePDF.paragrafo(str_pagina % cf(pagina, int)[1], PolePDF.pequena_direita)],
                       borda = False, posicao = (1 * cm, 0.55 * cm))
            pdf.celula(largura_folha, 1, None,
                       [PolePDF.paragrafo(str_agora, PolePDF.pequena_direita)],
                       borda = False, posicao = (1 * cm, 0.73 * cm))
        else:
            # Pula 1 cm
            pdf.celula(largura_folha, 1 * cm, '', '', borda = False)
        # Rederiza as céluas do sumário
        for celula in sumario:
            pdf.celula(*celula)
    # Caso solicitado a finalização, salva o pdf e mostrar para o usuário
    if finalizar:
        pdf.salvar()
        pdf.mostrar()
    # Retorna o pdf criado
    return pdf

LINHA = 0
PIZZA = 1
BARRAS = 2
ASCENDENTE = False
DESCENDENTE = True


def remove_columns(tuple, columns):
    row = list(tuple)

    for column in reversed(columns):
        row.pop(column)

    return row


def grafico(rotulos_valores, tipo = PIZZA, tamanho = (500, 500),
            rgb_fundo = (1, 1, 0.9), rgb_retangulo = (0.9, 0.9, 0.9),
            rgb_conteudo = (0, 0, 0.5), rgb_texto = (1, 1, 0),
            fundo_escala = None, percentual = True, ordem = None):
    "Retorna um gráfico em PNG dentro de um cStringIO"
    # Suporte gráfico com Cairo
    import cairo
    from math import pi, log
    largura, altura = tamanho
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, largura, altura)
    cr = cairo.Context(surface)
    # Fundo branco
    cr.set_source_rgb(*rgb_fundo)
    cr.paint()
    if ordem is not None:
        rotulos_valores = sorted(rotulos_valores, key=lambda x: x[1], reverse = ordem)
    if tipo == PIZZA:
        # Círculo, raio 5% menor
        raio = min(largura, altura) * 0.475
        cr.translate(largura / 2., altura / 2.)
        cr.set_source_rgb(*rgb_conteudo)
        cr.arc(0, 0, raio, 0, 2 * pi)
        cr.fill()
        cr.stroke()
        # Divisão do círculo
        cr.set_line_width(raio / 100.)
        cr.set_source_rgb(0, 0, 0)
        p = 0
        total = float(sum(zip(*rotulos_valores)[1]))
        for rotulo, valor in rotulos_valores:
            percentual = valor / total
            cr.move_to(0, 0)
            cr.arc(0, 0, raio, p * 2 * pi, (p + percentual) * 2 * pi)
            cr.save()
            if percentual:
                texto = "%s %.2f%%" % (rotulo, percentual * 100.)
            else:
                texto = "%s %.2f%%" % (rotulo, valor)
            size = raio / 10.
            height = size
            altura_maxima = 0
            while height - 2 > altura_maxima:
                cr.set_font_size(size)
                x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(texto)
                distancia = 0.95 * raio - width
                altura_maxima = percentual * pi * distancia
                size -= 1
            angulo = (p + percentual / 2) * 2 * pi
            if pi / 2 < angulo < 3 * pi / 2:
                cr.rotate(angulo + pi)
                cr.move_to(-0.95 * raio - x_bearing, height/2.)
            else:
                cr.rotate(angulo)
                cr.move_to(0.95 * raio - width - x_bearing, height/2.)
            cr.set_source_rgb(*rgb_texto)
            cr.show_text(texto)
            cr.restore()
            p += percentual
        cr.stroke()
    else: # BARRAS ou LINHAS desenha o retângulo
        maior = max(zip(*rotulos_valores)[1])
        if not fundo_escala:
            exp = 10. ** int(log(maior, 10))
            fundo_escala = (int(maior / exp) + 1) * exp
        parte_escala = fundo_escala / 10.
        if maior > fundo_escala * 0.95:
            partes = int(maior / parte_escala) + 1
            escala = partes * parte_escala
            if maior > escala * 0.95:
                escala += parte_escala
                partes += 1
        else:
            escala = fundo_escala
            partes = 10
        cr.translate(0.025 * largura, 0.975 * altura)
        n = len(rotulos_valores)
        w = largura * 0.95
        wo = w / (n * 3 + 1)
        wi = wo * 2
        h = -altura * 0.95
        cr.set_line_width(-h / 200.)
        cr.rectangle(0, 0, w, h)
        cr.set_source_rgb(*rgb_retangulo)
        cr.fill()
        cr.stroke()
        cr.rectangle(0, 0, w, h)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        cr.set_line_width(-h / 1000.)
        for i in range(1, partes):
            cr.move_to(0, h * i / partes)
            cr.line_to(w, h * i / partes)
        cr.stroke()
        for i, (rotulo, valor) in enumerate(rotulos_valores):
            cr.rectangle(wo + (wi + wo) * i, 0, wi, valor/escala * h)
            cr.set_source_rgb(*rgb_conteudo)
            cr.fill()
            cr.stroke()
            cr.save()
            cr.set_font_size(wo)
            x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(rotulo)
            if valor / escala * h - wo - x_advance - 20 > h:
                cr.move_to(wo + (wi + wo) * i + wi / 2 + height / 2, valor / escala * h - wo)
            else:
                cr.move_to(wo + (wi + wo) * i + wi / 2 + height / 2, valor / escala * h + wo + x_advance)
            cr.rotate(-pi / 2)
            cr.set_source_rgb(*rgb_texto)
            cr.show_text(rotulo)
            cr.restore()

    # Retornar PNG em cStringIO
    png_file = cStringIO.StringIO()
    surface.write_to_png(png_file)
    png_file.seek(0)
    return png_file

# Exemplo de uso
if  __name__ == "__main__":
    pdf = gerar_pdf(None,
              '01/01/2011',
              '31/03/2011',
              "Relatórios de Recursos Cadastrado",
              [['Cód. Recurso', 1.5, 'str'],
               ['Descrição', 1.5, 'str', 'set'],
               ['Valor Hora 1', 3, 'str', 'len'],
               ['Valor Hora 2', 3.5, 'str'],
               ['Valor Hora 3', 6, 'int', 'sum'],
               ['Valor Hora 4', 3, 'float', '3', 'sum'],
               ['Valor Hora 5', 3, 'int', 'perc 4 5'],
               ['Valor Hora 6', 3, 'Quebrado 2', 'sum'],
               ['Ativo', 3, 'bool', 'set'],
              ],
              '',
              [[123,'Hora 1',5465,123465,1,2,3,4,True] ,
               [123,'Hora 2',5465,123465,1,2,3,4,False],
               [123,'Hora 3',5465,123465,1,2,3,100,True] ,
               [123,'Hora 4',5465,123465,1,2,3,4,True]] * 25,
              None,
              sumario = [[5 * cm, 1 * cm, "Titulo 1", "Inform 24"],
                         [7 * cm, 0.1 * cm, "Titulo 2", "Inform 23"],
                         [9 * cm, 0.1 * cm, "Titulo 3", "Inform 22"],
                         [6.7 * cm, 0.1 * cm, "Titulo 4", "Inform 21"],
                         [5 * cm, 0.1 * cm, "Titulo 5", "Inform 20"],
                         [7 * cm, 0.1 * cm, "Titulo 6", "Inform 19"],
                         [9 * cm, 0.1 * cm, "Titulo 7", "Inform 18"],
                         [6.7 * cm, 5 * cm, "Titulo 8", "Inform 17"],
                         [5 * cm, 0.1 * cm, "Titulo 9", "Inform 16"],
                         [7 * cm, 0.1 * cm, "Titulo 10", "Inform 15"],
                         [9 * cm, 0.1 * cm, "Titulo 11", "Inform 14"],
                         [6.7 * cm, 0.1 * cm, "Titulo 12", "Inform 13"],
                        ],
            finalizar  = False)

    pdf.celula(10 * cm, 5 * cm, "", "Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- Este é um teste que vai ter que ficar lá ---- ")#, alinhamento = "direita")
    pdf.celula(3 * cm, 1 * cm, "", "Abaixo terá os gráficos ao lado em tamanho grande")

    png = grafico([['Ígor', 61245.67],
                   ['Claudio', 234567.89],
                   ['Élio', 12345.67],
                   ['Alexandre', 54654.45],
                   ['Freddy', 439224.24]],
                  tipo = PIZZA,
                  ordem = DESCENDENTE)

    png2 = grafico([['Ígor', 61245.67],
                    ['Claudio', 234567.89],
                    ['Élio', 12345.67],
                    ['Alexandre', 54654.45],
                    ['Freddy', 439224.24]],
                   tipo = BARRAS,
                   tamanho = (850, 600),
                   ordem = None,
                   #rgb_fundo = (0,0,0),
                   )

    # Para ver a imagem gerada e tamanho num arquivo
    open('/tmp/pole_relatorio.png', 'wb').write(png.getvalue())
    open('/tmp/pole_relatorio2.png', 'wb').write(png2.getvalue())

    img = PolePDF.Image(png)
    img.drawWidth = 5 * cm
    img.drawHeight = img.drawWidth
    pdf.celula(img.drawWidth, 1 * cm, None, [img], borda = True)

    img2 = PolePDF.Image(png2)
    img2.drawWidth *= 7 * cm / img2.drawHeight
    img2.drawHeight = 7 * cm
    pdf.celula(img2.drawWidth, 1 * cm, None, [img2], borda = True)

    pdf.nova_pagina()
    img.drawWidth = 20 * cm
    img.drawHeight = img.drawWidth
    pdf.celula(img.drawWidth, 1 * cm, None, [img], borda = False,
               posicao = ((pdf.canvas._pagesize[0] - img.drawWidth) / 2,
                          (pdf.canvas._pagesize[1] - img.drawHeight) / 2))

    pdf.nova_pagina()
    img2.drawWidth *= 20 * cm / img2.drawHeight
    img2.drawHeight = 20 * cm
    pdf.celula(img2.drawWidth, 1 * cm, None, [img2], borda = False,
               posicao = ((pdf.canvas._pagesize[0] - img2.drawWidth) / 2,
                          (pdf.canvas._pagesize[1] - img2.drawHeight) / 2))

    pdf.salvar()
    pdf.mostrar()

