"""Small vector teaching diagrams, computed from validated mathematical data."""
from fractions import Fraction
from math import isfinite, lcm
from statistics import median
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

KINDS = ('fraction_groups', 'unit_rate', 'inequality', 'coordinates', 'prism_net', 'dot_plot')


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'Diagram integer must be in {low}..{high}')
    return value


def pair(value, low, high):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError('Diagram requires a pair')
    return tuple(integer(v, low, high) for v in value)


def model(spec):
    """Return computed results; constrain supported ranges to legible layouts."""
    if not isinstance(spec, dict) or spec.get('kind') not in KINDS:
        raise ValueError('Unknown diagram kind')
    kind = spec['kind']
    if kind == 'fraction_groups':
        a, b = pair(spec.get('dividend'), 1, 12)
        c, d = pair(spec.get('divisor'), 1, 12)
        dividend, divisor = Fraction(a,b), Fraction(c,d)
        grid=lcm(b,d)
        if dividend > 1 or divisor > 1 or grid > 12:
            raise ValueError('Fraction model requires at most twelve cells within one whole')
        return dict(kind=kind, numerator=int(dividend*grid), denominator=grid, group_cells=int(divisor*grid),
                    quotient=str(dividend/divisor), dividend=str(dividend), divisor=str(divisor))
    if kind == 'unit_rate':
        quantity = integer(spec.get('quantity'), 1, 10)
        total = integer(spec.get('total'), 1, 1000)
        target = integer(spec.get('target'), 1, 10)
        return dict(kind=kind, quantity=quantity, total=total, target=target,
                    unit_rate=str(Fraction(total, quantity)), target_cost=str(Fraction(total,quantity)*target))
    if kind == 'inequality':
        boundary = integer(spec.get('boundary'), 1, 10000)
        if spec.get('operator') not in ('<', '<=', '>', '>='):
            raise ValueError('Invalid inequality operator')
        return dict(kind=kind, boundary=boundary, operator=spec['operator'],
                    included='=' in spec['operator'], left=spec['operator'].startswith('<'))
    if kind == 'coordinates':
        start = pair(spec.get('start'), -3, 3)
        shift = integer(spec.get('shift_x'), -6, 6)
        moved = (start[0]+shift, start[1])
        if not -4 <= moved[0] <= 4 or spec.get('reflect') != 'x':
            raise ValueError('Coordinate model supports reflection across x within the grid')
        if start[1] == 0:
            raise ValueError('Reflection example must move off the x-axis')
        return dict(kind=kind, start=start, moved=moved, reflected=(moved[0],-moved[1]))
    if kind == 'prism_net':
        dimensions = spec.get('dimensions')
        if not isinstance(dimensions, list) or len(dimensions) != 3:
            raise ValueError('Prism needs three dimensions')
        l,w,h = (integer(v, 1, 9) for v in dimensions)
        return dict(kind=kind, dimensions=(l,w,h), surface_area=2*(l*w+l*h+w*h), volume=l*w*h)
    values = spec.get('values')
    if not isinstance(values,list) or not 2 <= len(values) <= 12:
        raise ValueError('Dot plot requires 2..12 values')
    values = [integer(v, 0, 100) for v in values]
    if min(values) == max(values) or max(values.count(v) for v in values) > 3:
        raise ValueError('Dot plot requires spread and at most three stacked dots')
    unique = sorted(set(values))
    if len(unique) > 6:
        raise ValueError('Dot plot supports at most six distinct values')
    differences = {b-a for a,b in zip(unique,unique[1:])}
    if len(differences) != 1:
        raise ValueError('Dot plot values must form uniformly spaced ticks')
    return dict(kind=kind, values=values, ticks=unique, mean=str(Fraction(sum(values),len(values))),
                mad=str(sum(abs(Fraction(v)-Fraction(sum(values),len(values))) for v in values)/len(values)),
                median=median(values), frequencies={str(v):values.count(v) for v in unique})


def render(c, spec, x, y, width, height, theme):
    """Render within a measured viewport. All labels remain editable PDF text."""
    data = model(spec)
    if not all(isinstance(v,(int,float)) and isfinite(v) for v in (x,y,width,height)) or width < 450 or height < 70:
        raise ValueError('Diagram viewport too small or invalid')
    ink = HexColor('#183354')
    accent = HexColor('#E6632F' if theme == 'playful-illustrated' else '#286E9C')
    pale = HexColor('#FFFFFF')
    c.saveState()
    c.translate(x,y)

    def text(px,py,value,size=8,bold=False):
        font = 'LessonBold' if bold else 'LessonRegular'
        value = str(value)
        if px < 0 or py < 0 or py+size > height or px+pdfmetrics.stringWidth(value,font,size) > width:
            raise ValueError('Diagram label exceeds viewport')
        c.setFillColor(ink); c.setFont(font,size); c.drawString(px,py,value)

    def line(x1,y1,x2,y2,color=ink,weight=1):
        c.setStrokeColor(color);c.setLineWidth(weight);c.line(x1,y1,x2,y2)

    def arrow(x1,y1,x2,y2):
        from math import atan2, sin, cos
        line(x1,y1,x2,y2,accent,1.5)
        angle=atan2(y2-y1,x2-x1)
        for delta in (-.55,.55):
            line(x2,y2,x2-5*cos(angle+delta),y2-5*sin(angle+delta),accent,1.5)

    kind=data['kind']
    if kind == 'fraction_groups':
        cell=240/data['denominator']
        for i in range(data['denominator']):
            c.setFillColor(accent if i<data['numerator'] else pale)
            c.setStrokeColor(ink);c.rect(8+i*cell,28,cell,24,fill=1,stroke=1)
        group=float(data['group_cells'])*cell
        line(8,22,8+group,22,ink,2)
        text(8,7,f"One group = {data['divisor']}")
        text(270,44,f"Shaded amount: {data['dividend']}")
        text(270,24,f"Groups that fit: {data['quotient']}",bold=True)
    elif kind == 'unit_rate':
        maximum=max(data['quantity'],data['target'])
        positions=sorted(set((0,1,data['quantity'],data['target'])))
        text(0,55,'Filters');text(0,19,'Cost ($)')
        for baseline in (51,17):line(74,baseline,330,baseline)
        for n in positions:
            px=78+246*n/maximum
            for baseline in (51,17):line(px,baseline-3,px,baseline+3)
            text(px-3,60,n,7)
            text(px-3,3,Fraction(data['unit_rate'])*n,7)
        text(350,43,f"${data['unit_rate']} per filter",bold=True)
        text(350,24,f"{data['target']} filters: ${data['target_cost']}")
    elif kind == 'inequality':
        boundary=data['boundary'];left=data['left']
        start,end,base=15,325,32
        line(start,base,end,base)
        pivot=start+(end-start)*2/3
        values=(0, Fraction(boundary,2), boundary, Fraction(3*boundary,2))
        for px,n in zip((start,(start+pivot)/2,pivot,end),values):
            line(px,base-4,px,base+4);text(max(0,px-12),12,n,7)
        arrow(pivot-7 if left else pivot+7,base,start if left else end,base)
        c.setStrokeColor(accent);c.setFillColor(accent if data['included'] else pale)
        c.circle(pivot,base,4,fill=1,stroke=1)
        text(350,43,'Boundary included' if data['included'] else 'Boundary excluded',bold=True)
        text(350,24,f"w {data['operator']} {boundary}")
    elif kind == 'coordinates':
        ox,oy,step=95,35,9
        for n in range(-4,5):line(ox+n*step,oy-27,ox+n*step,oy+27,HexColor('#C6D3DF'),.4)
        for n in range(-3,4):line(ox-36,oy+n*step,ox+36,oy+n*step,HexColor('#C6D3DF'),.4)
        arrow(ox-40,oy,ox+42,oy);arrow(ox,oy-30,ox,oy+31)
        text(139,oy-3,'x',7);text(ox+4,60,'y',7)
        points=[data['start'],data['moved'],data['reflected']]
        for a,b in zip(points,points[1:]):arrow(ox+a[0]*step,oy+a[1]*step,ox+b[0]*step,oy+b[1]*step)
        for label,point in zip(('A','B','C'),points):
            px,py=ox+point[0]*step,oy+point[1]*step
            c.setFillColor(accent);c.circle(px,py,2.5,fill=1,stroke=0);text(px+4,py+3,label,7,True)
        text(180,51,f"A {data['start']} -> B {data['moved']}")
        text(180,32,f"Reflect B across x-axis: C {data['reflected']}")
        text(180,13,'Each grid step is 1 unit.')
    elif kind == 'prism_net':
        l,w,h=data['dimensions']
        scale=min(7,62/(2*w+h),200/(2*l+2*w))
        sx,sy=12,4+w*scale
        faces=[(0,0,l,h),(l,0,w,h),(l+w,0,l,h),(2*l+w,0,w,h),(0,h,l,w),(0,-w,l,w)]
        for dx,dy,fw,fh in faces:
            c.setStrokeColor(ink);c.setFillColor(pale)
            c.rect(sx+dx*scale,sy+dy*scale,fw*scale,fh*scale,fill=1,stroke=1)
            label=f'{fw}x{fh}'
            if pdfmetrics.stringWidth(label,'LessonRegular',8)>fw*scale-4 or fh*scale<12:
                raise ValueError('Prism faces too small for readable labels')
            text(sx+dx*scale+2,sy+dy*scale+(fh*scale-8)/2,label,8)
        text(240,49,'Six faces unfold into a net.',bold=True)
        text(240,30,f"Surface area: {data['surface_area']} square inches")
        text(240,11,f"Volume: {data['volume']} cubic inches")
    else:
        ticks=data['ticks'];step=240/(len(ticks)-1)
        line(15,16,270,16)
        for i,n in enumerate(ticks):
            px=24+i*step
            line(px,13,px,19);text(px-6,1,n,7)
            for j in range(data['frequencies'][str(n)]):
                c.setFillColor(accent);c.circle(px,27+j*12,3.5,fill=1,stroke=0)
        text(300,50,'Repair times (minutes)',bold=True)
        text(300,31,f"Median: {data['median']}")
        text(300,12,f"Mean: {data['mean']}")
    c.restoreState()
    return data
