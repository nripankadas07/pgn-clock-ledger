"""Explain mainline PGN clock evidence under a simple after-move increment convention."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES=128*1024
TAG=re.compile(r'\[([A-Za-z][A-Za-z0-9_]*)\s+"((?:[^"\\\r\n]|\\["\\])*)"\s*\]')
CLOCK=re.compile(r'\[%clk\s+([0-9]{1,2}):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,3}))?\]')
MOVE=re.compile(r'(?:O-O(?:-O)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?)(?:\+\+|[+#])?[!?]{0,2}\Z')
RESULTS={'1-0','0-1','1/2-1/2','*'}

def analyze(text):
    if len(text.encode('utf-8'))>MAX_BYTES or '\0' in text:raise ValueError('PGN exceeds128KiB or contains NUL')
    pos=0;headers={}
    while True:
        while pos<len(text) and text[pos].isspace():pos+=1
        if pos>=len(text) or text[pos]!='[':break
        m=TAG.match(text,pos)
        if not m or len(headers)>=64 or m[1] in headers or len(m[2])>1024:raise ValueError('invalid, duplicate or oversized PGN header')
        headers[m[1]]=re.sub(r'\\(["\\])',r'\1',m[2]);pos=m.end()
    tc=re.fullmatch(r'([0-9]{1,5})\+([0-9]{1,4})',headers.get('TimeControl',''))
    if not tc or not 1<=int(tc[1])<=86400 or not 0<=int(tc[2])<=3600:raise ValueError('TimeControl must be simple base+increment seconds, base1..86400/increment0..3600')
    if 'FEN' in headers or 'SetUp' in headers or headers.get('Variant','Standard')!='Standard':raise ValueError('nonstandard starts/variants unsupported')
    base,increment=1000*int(tc[1]),1000*int(tc[2])
    plies=[];depth=0;result=None;pending_number=False
    while pos<len(text):
        c=text[pos]
        if c.isspace():pos+=1;continue
        if c==';' or (c=='%' and (pos==0 or text[pos-1] in '\r\n')):
            newline=text.find('\n',pos);pos=len(text) if newline<0 else newline+1;continue
        if c=='{':
            end=text.find('}',pos+1)
            if end<0 or '{' in text[pos+1:end]:raise ValueError('unclosed or nested brace comment')
            comment=text[pos+1:end];pos=end+1
            if depth:continue
            clocks=list(CLOCK.finditer(comment))
            if comment.count('[%clk')!=len(clocks):raise ValueError('malformed clock annotation')
            if clocks:
                if len(clocks)!=1 or not plies or result is not None or pending_number or plies[-1]['clock_millis'] is not None:raise ValueError('clock must follow exactly one mainline move; duplicate/leading clocks refused')
                m=clocks[0];milliseconds=((int(m[1])*60+int(m[2]))*60+int(m[3]))*1000+int((m[4] or '').ljust(3,'0') or '0')
                plies[-1]['clock_millis']=milliseconds
            continue
        if c=='(':
            if result is not None or not plies or depth>=32:raise ValueError('variation placement/depth invalid')
            depth+=1;pos+=1;continue
        if c==')':
            if not depth:raise ValueError('unbalanced variation')
            depth-=1;pos+=1;continue
        if c in '[]}' or (c=='%' and not depth):raise ValueError('unexpected PGN delimiter; one game only')
        end=pos
        while end<len(text) and not text[end].isspace() and text[end] not in '{}();[]':end+=1
        token=text[pos:end];pos=end
        if len(token)>64 or not token:raise ValueError('unsupported or oversized movetext token')
        if depth:continue
        if result is not None:raise ValueError('movetext follows game terminator')
        if re.fullmatch(r'\$[0-9]{1,4}',token):
            if not plies:raise ValueError('annotation before any move')
            continue
        m=re.match(r'([0-9]{1,5})(\.\.\.|\.)',token)
        if m:
            expected=len(plies)//2+1;side='white' if len(plies)%2==0 else 'black'
            if pending_number or int(m[1])!=expected or (m[2]=='...')!=(side=='black'):raise ValueError('mainline move number/side mismatch')
            pending_number=True;token=token[m.end():]
            if not token:continue
        if token in RESULTS:
            if pending_number:raise ValueError('move number without move')
            result=token;continue
        if not MOVE.fullmatch(token) or len(plies)>=10000:raise ValueError('unsupported SAN-like label or ply budget')
        plies.append({'ply':len(plies)+1,'move_number':len(plies)//2+1,'side':'white' if len(plies)%2==0 else 'black','move':token,'clock_millis':None})
        pending_number=False
    if depth or pending_number or result is None or not plies:raise ValueError('one terminated nonempty mainline with balanced variations required')
    if 'Result' in headers and headers['Result']!=result:raise ValueError('header and movetext results differ')
    previous={'white':base,'black':base};totals=dict.fromkeys(previous,0);computed=dict.fromkeys(previous,0);findings=[]
    for item in plies:
        side=item['side'];clock=item['clock_millis'];prior=previous[side];item['prior_same_side_clock_millis']=prior;item['increment_millis']=increment;item['elapsed_millis']=None
        if clock is None:status='clock_missing';previous[side]=None
        elif prior is None:status='prior_clock_missing';previous[side]=clock
        elif clock>prior+increment:status='clock_increase_exceeds_increment';previous[side]=clock
        else:
            status='computed_under_increment_convention';item['elapsed_millis']=prior+increment-clock;previous[side]=clock;totals[side]+=item['elapsed_millis'];computed[side]+=1
        item['status']=status
        if status!='computed_under_increment_convention':findings.append({'ply':item['ply'],'side':side,'reason':status})
    return {'time_control':{'base_millis':base,'increment_millis':increment,'assumption':'Every captured clock is after that move and its increment; no delay, stages or flag convention inferred.'},
        'result':result,'plies':plies,'known_elapsed_totals_millis':totals,'computed_plies':computed,'findings':findings,'ignored_header_keys':sorted(set(headers)-{'TimeControl','Result'}),
        'scope':'Clock evidence over alternating mainline labels, not chess legality, engine evaluation, actual thinking/network time, flag or cheating inference. Variations and semicolon comments do not contribute clock evidence. Missing clocks invalidate only the next same-side difference until a new baseline is captured.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');a=p.parse_args()
    try:
        with Path(a.input).open('rb') as f:raw=f.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError('PGN exceeds128KiB')
        r=analyze(raw.decode('utf-8-sig'));print(json.dumps(r,sort_keys=True,indent=2));return int(bool(r['findings']))
    except (ValueError,OSError,UnicodeError,OverflowError,RecursionError) as e:
        print(json.dumps({'error':str(e)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
