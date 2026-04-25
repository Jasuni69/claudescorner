// scenes.jsx — Clementine Analytics process video scenes
// Global components attached to window at bottom.

const BRAND = {
  paper: '#FBF7F1',
  ink: '#0B0B10',
  accent: '#F26A1F',
  accentDeep: '#C14A10',
  accentSoft: '#FFD3B0',
  muted: 'rgba(251,247,241,.55)',
};

// The segmented clementine mark (matches brand logo)
function ClementineMark({ size = 160, rotation = 0, style = {} }) {
  return (
    <svg width={size} height={size} viewBox="-50 -50 100 100" style={{ transform: `rotate(${rotation}deg)`, ...style }}>
      {[-72, -36, 0, 36, 72].map((r, i) => (
        <g key={i} transform={`rotate(${r})`}>
          <path
            d="M 10 -6 L 44 -10 A 45 45 0 0 1 44 10 L 10 6 A 11 11 0 0 0 10 -6 Z"
            fill={i % 2 === 0 ? '#F58233' : '#F37323'}
          />
        </g>
      ))}
    </svg>
  );
}

// A source-system logo card (placeholder — designed to hold a real product screenshot later)
// Pass `image` to swap in a real screenshot/logo file.
function SystemChip({ name, subtitle, delay, x, y, width = 280, image = null }) {
  const t = useTime();
  const rel = t - delay;
  const opacity = rel < 0 ? 0 : Math.min(1, rel / 0.35);
  const ty = rel < 0 ? 20 : Math.max(0, 20 - (rel / 0.35) * 20);

  // initials for placeholder glyph
  const initials = name
    .split(/\s+/)
    .map(w => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div style={{
      position: 'absolute', left: x, top: y, width,
      opacity, transform: `translateY(${ty}px)`,
      background: 'rgba(251,247,241,0.05)',
      border: '1px solid rgba(251,247,241,0.14)',
      borderRadius: 14,
      padding: '14px 16px',
      color: BRAND.paper,
      fontFamily: 'Onest, system-ui, sans-serif',
      display: 'flex', alignItems: 'center', gap: 14,
      backdropFilter: 'blur(6px)',
      boxShadow: '0 6px 20px rgba(0,0,0,.18)',
    }}>
      {/* Logo slot — swap `image` to use a real PNG/SVG */}
      <div style={{
        width: 52, height: 52, borderRadius: 12,
        background: image ? 'transparent' : 'linear-gradient(145deg, rgba(251,247,241,.12), rgba(251,247,241,.04))',
        border: image ? 'none' : '1px dashed rgba(251,247,241,.25)',
        flex: '0 0 auto',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        overflow: 'hidden',
      }}>
        {image ? (
          <img src={image} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }}/>
        ) : (
          <span style={{
            fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
            fontSize: 20, fontWeight: 600, letterSpacing: '-.01em',
            color: BRAND.accentSoft,
          }}>{initials}</span>
        )}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0, flex: 1 }}>
        <div style={{ fontSize: 20, fontWeight: 600, color: BRAND.paper, letterSpacing: '-.01em' }}>
          {name}
        </div>
        <div style={{ fontSize: 12, color: 'rgba(251,247,241,.55)', letterSpacing: '.04em' }}>
          {subtitle || 'Källsystem'}
        </div>
      </div>
      <div style={{
        width: 6, height: 6, borderRadius: 6,
        background: BRAND.accent, flex: '0 0 auto',
        boxShadow: `0 0 8px ${BRAND.accent}`,
      }}/>
    </div>
  );
}

// Data particle streaming across
function Particle({ fromX, fromY, toX, toY, start, duration, color = BRAND.accent }) {
  const t = useTime();
  const rel = (t - start) / duration;
  if (rel < 0 || rel > 1.15) return null;
  const p = Math.max(0, Math.min(1, rel));
  const eased = Easing.easeInOutCubic(p);
  const x = fromX + (toX - fromX) * eased;
  const y = fromY + (toY - fromY) * eased;
  const opacity = rel < 0.1 ? rel * 10 : rel > 0.9 ? (1 - rel) * 10 : 1;
  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      width: 8, height: 8, borderRadius: 8,
      background: color,
      boxShadow: `0 0 20px ${color}, 0 0 8px ${color}`,
      opacity,
      transform: 'translate(-50%, -50%)',
    }}/>
  );
}

// A product-screenshot placeholder card (designed to be swapped for a real screenshot later)
// Pass `image` to display an actual screenshot in place of the placeholder chart.
function DashCard({ title, kind, x, y, delay, width = 340, height = 210, image = null }) {
  const t = useTime();
  const rel = t - delay;
  const opacity = rel < 0 ? 0 : Math.min(1, rel / 0.4);
  const eased = Easing.easeOutBack(Math.min(1, Math.max(0, rel / 0.5)));
  const s = 0.9 + eased * 0.1;

  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      width, height,
      opacity, transform: `scale(${s})`,
      background: BRAND.paper,
      borderRadius: 14,
      boxShadow: '0 18px 40px rgba(0,0,0,.35), 0 4px 12px rgba(0,0,0,.2)',
      color: BRAND.ink,
      fontFamily: 'Onest, system-ui, sans-serif',
      overflow: 'hidden',
      display: 'flex', flexDirection: 'column',
      border: '1px solid rgba(11,11,16,.08)',
    }}>
      {/* Browser-style chrome */}
      <div style={{
        padding: '10px 14px',
        background: 'rgba(11,11,16,.04)',
        borderBottom: '1px solid rgba(11,11,16,.06)',
        display: 'flex', alignItems: 'center', gap: 6,
        flex: '0 0 auto',
      }}>
        <span style={{ width: 8, height: 8, borderRadius: 8, background: '#FF6159' }}/>
        <span style={{ width: 8, height: 8, borderRadius: 8, background: '#FFBD2E' }}/>
        <span style={{ width: 8, height: 8, borderRadius: 8, background: '#2ACA3E' }}/>
        <span style={{
          marginLeft: 10,
          fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase',
          color: 'rgba(11,11,16,.5)', fontWeight: 500,
        }}>{kind}</span>
      </div>

      {image ? (
        <img src={image} alt={kind} style={{ width: '100%', height: '100%', objectFit: 'cover', flex: 1 }}/>
      ) : (
        <ChartPlaceholder title={title} kind={kind} delay={delay} />
      )}
    </div>
  );
}

// Animated, chart-like placeholder (so designers see motion in the hero embed
// before real screenshots are dropped in).
function ChartPlaceholder({ title, kind, delay }) {
  const t = useTime();
  const phase = Math.max(0, t - delay - 0.3);

  // Pick a chart style based on kind
  const style =
    /sälj/i.test(kind) ? 'line' :
    /balans/i.test(kind) ? 'donut' :
    'bars';

  return (
    <div style={{
      flex: 1,
      padding: '12px 14px 14px',
      display: 'flex', flexDirection: 'column', gap: 6,
      minHeight: 0,
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      }}>
        <div style={{
          fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
          fontSize: 22, fontWeight: 500, letterSpacing: '-.01em',
          color: BRAND.ink,
        }}>{title}</div>
        <div style={{
          fontSize: 10, letterSpacing: '.1em', color: 'rgba(11,11,16,.45)',
          fontWeight: 500,
        }}>Q4 · 2025</div>
      </div>

      <div style={{ flex: 1, minHeight: 0, display: 'flex', alignItems: 'stretch' }}>
        {style === 'bars' && <PlaceholderBars phase={phase} />}
        {style === 'line' && <PlaceholderLine phase={phase} />}
        {style === 'donut' && <PlaceholderDonut phase={phase} />}
      </div>
    </div>
  );
}

function PlaceholderBars({ phase }) {
  const base = [0.45, 0.72, 0.58, 0.9, 0.68, 0.82, 0.95];
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, width: '100%' }}>
      {base.map((v, i) => {
        const grow = Math.min(1, Math.max(0, (phase - i * 0.05) / 0.5));
        const h = v * grow;
        const isHero = i === base.length - 1;
        return (
          <div key={i} style={{
            flex: 1,
            height: `${h * 100}%`,
            background: isHero ? BRAND.accent : 'rgba(242,106,31,.28)',
            borderRadius: 3,
          }}/>
        );
      })}
    </div>
  );
}

function PlaceholderLine({ phase }) {
  const pts = [0.2, 0.35, 0.28, 0.5, 0.45, 0.62, 0.58, 0.78, 0.72, 0.9];
  const w = 260, h = 100;
  const step = w / (pts.length - 1);
  const toXY = (v, i) => [i * step, h - v * h];
  const progress = Math.min(1, phase / 1.0);
  const visCount = Math.max(1, Math.floor(pts.length * progress));
  const visible = pts.slice(0, visCount);

  const pathD = visible.map((v, i) => {
    const [x, y] = toXY(v, i);
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  const areaD = visible.length
    ? pathD + ` L ${(visible.length - 1) * step} ${h} L 0 ${h} Z`
    : '';

  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
      {/* grid */}
      {[0.25, 0.5, 0.75].map(g => (
        <line key={g} x1={0} x2={w} y1={h * g} y2={h * g}
          stroke="rgba(11,11,16,.08)" strokeWidth={1}/>
      ))}
      <path d={areaD} fill={`${BRAND.accent}22`}/>
      <path d={pathD} fill="none" stroke={BRAND.accent} strokeWidth={2.5}
        strokeLinecap="round" strokeLinejoin="round"/>
      {visible.map((v, i) => {
        const [x, y] = toXY(v, i);
        return <circle key={i} cx={x} cy={y} r={2.5} fill={BRAND.accent}/>;
      })}
    </svg>
  );
}

function PlaceholderDonut({ phase }) {
  const progress = Math.min(1, phase / 1.0);
  const circ = 2 * Math.PI * 34;
  // three segments totalling ~ circle
  const segs = [
    { frac: 0.45, color: BRAND.accent },
    { frac: 0.30, color: `${BRAND.accent}99` },
    { frac: 0.25, color: `${BRAND.accent}55` },
  ];
  let offset = 0;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, width: '100%' }}>
      <svg width={90} height={90} viewBox="0 0 90 90">
        <circle cx={45} cy={45} r={34} fill="none" stroke="rgba(11,11,16,.08)" strokeWidth={10}/>
        {segs.map((s, i) => {
          const dash = s.frac * circ * progress;
          const el = (
            <circle key={i} cx={45} cy={45} r={34} fill="none"
              stroke={s.color} strokeWidth={10}
              strokeDasharray={`${dash} ${circ - dash}`}
              strokeDashoffset={-offset}
              transform="rotate(-90 45 45)"
              strokeLinecap="butt"/>
          );
          offset += s.frac * circ;
          return el;
        })}
      </svg>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {segs.map((s, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            fontSize: 11, color: 'rgba(11,11,16,.7)',
            opacity: Math.min(1, Math.max(0, (phase - 0.3 - i * 0.1) / 0.3)),
          }}>
            <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color }}/>
            <span style={{ fontWeight: 500 }}>
              {i === 0 ? 'Tillgångar' : i === 1 ? 'Skulder' : 'Eget kapital'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============== MAIN SCENES ==============

function SceneIntro() {
  // 0 - 3.5s: tagline
  return (
    <Sprite start={0} end={3.8}>
      {({ localTime }) => {
        const t1 = Math.min(1, localTime / 0.6);
        const t2 = Math.min(1, Math.max(0, localTime - 0.35) / 0.6);
        const t3 = Math.min(1, Math.max(0, localTime - 0.7) / 0.6);
        const exitT = Math.min(1, Math.max(0, localTime - 3.0) / 0.6);
        const exitY = -exitT * 40;
        const exitOpacity = 1 - exitT;

        return (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column',
            alignItems: 'flex-start', justifyContent: 'center',
            padding: '0 140px',
            opacity: exitOpacity,
            transform: `translateY(${exitY}px)`,
          }}>
            <div style={{
              fontFamily: 'Onest, system-ui, sans-serif',
              fontSize: 20, fontWeight: 500,
              letterSpacing: '.18em', textTransform: 'uppercase',
              color: BRAND.accent,
              opacity: t1, transform: `translateY(${(1 - t1) * 14}px)`,
              marginBottom: 28,
              display: 'flex', alignItems: 'center', gap: 16,
            }}>
              <span style={{ width: 36, height: 2, background: BRAND.accent, display: 'inline-block' }}/>
              Produktlösning
            </div>
            <div style={{
              fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
              fontSize: 116, fontWeight: 500,
              letterSpacing: '-.035em', lineHeight: 0.95,
              color: BRAND.paper,
            }}>
              <div style={{ opacity: t1, transform: `translateY(${(1 - t1) * 30}px)` }}>
                Hoppa över
              </div>
              <div style={{ opacity: t2, transform: `translateY(${(1 - t2) * 30}px)` }}>
                BI-resan.
              </div>
              <div style={{ opacity: t3, transform: `translateY(${(1 - t3) * 30}px)`, color: BRAND.accent, fontStyle: 'italic', fontWeight: 400 }}>
                Börja där andra slutar.
              </div>
            </div>
          </div>
        );
      }}
    </Sprite>
  );
}

function SceneProcess() {
  // 3.5s - 12s: systems → clementine → dashboards
  const t = useTime();
  const sceneStart = 3.5;
  const rel = t - sceneStart;

  if (rel < -0.3 || rel > 10) return null;

  // Header fade
  const headerT = Math.min(1, Math.max(0, rel / 0.5));
  const headerExitT = Math.min(1, Math.max(0, (rel - 8.4) / 0.5));

  return (
    <div style={{
      position: 'absolute', inset: 0,
      opacity: headerT * (1 - headerExitT),
    }}>
      {/* Header */}
      <div style={{
        position: 'absolute', top: 60, left: 80,
        fontFamily: 'Onest, system-ui, sans-serif',
        fontSize: 16, letterSpacing: '.18em', textTransform: 'uppercase',
        color: BRAND.accent, fontWeight: 500,
        display: 'flex', alignItems: 'center', gap: 14,
      }}>
        <span style={{ width: 36, height: 2, background: BRAND.accent }}/>
        Från era system till färdiga dashboards
      </div>

      {/* Column labels */}
      <ColLabel x={160} y={200} delay={sceneStart + 0.0} text="01 — Källor" />
      <ColLabel x={820} y={200} delay={sceneStart + 1.4} text="02 — Motor" />
      <ColLabel x={1440} y={200} delay={sceneStart + 3.2} text="03 — Leverans" />

      {/* Left: customer systems */}
      <SystemChip name="Fortnox"      subtitle="Bokföring" x={100} y={260} delay={sceneStart + 0.2} />
      <SystemChip name="Hailey HR"    subtitle="Personal"  x={100} y={348} delay={sceneStart + 0.45} />
      <SystemChip name="PowerOffice"  subtitle="Redovisning" x={100} y={436} delay={sceneStart + 0.7} />
      <SystemChip name="Dynamics 365" subtitle="ERP · Business Central" x={100} y={524} delay={sceneStart + 0.95} />

      {/* Middle: Clementine engine */}
      <ClementineEngine x={860} y={380} delay={sceneStart + 1.7} />

      {/* Particles flowing left → center */}
      {[
        { fy: 285, d: 0.9 },
        { fy: 373, d: 1.05 },
        { fy: 461, d: 1.2 },
        { fy: 549, d: 1.35 },
        { fy: 285, d: 1.9 },
        { fy: 373, d: 2.05 },
        { fy: 461, d: 2.2 },
        { fy: 549, d: 2.35 },
      ].map((p, i) => (
        <Particle
          key={`p-in-${i}`}
          fromX={380} fromY={p.fy}
          toX={860} toY={380}
          start={sceneStart + p.d}
          duration={1.1}
          color={BRAND.accent}
        />
      ))}

      {/* Particles flowing center → right */}
      {[
        { ty: 315, d: 3.0 },
        { ty: 500, d: 3.1 },
        { ty: 685, d: 3.2 },
        { ty: 315, d: 4.2 },
        { ty: 500, d: 4.3 },
        { ty: 685, d: 4.4 },
      ].map((p, i) => (
        <Particle
          key={`p-out-${i}`}
          fromX={960} fromY={380}
          toX={1460} toY={p.ty}
          start={sceneStart + p.d}
          duration={0.95}
          color={BRAND.accentSoft}
        />
      ))}

      {/* Right: dashboards (product-screenshot placeholders) */}
      <DashCard kind="Resultatrapport" title="+246 900 kr"  x={1400} y={240} delay={sceneStart + 3.6} />
      <DashCard kind="Balansrapport"   title="12,4 M kr"    x={1400} y={465} delay={sceneStart + 3.95} />
      <DashCard kind="Säljrapport"     title="34 st deals"  x={1400} y={690} delay={sceneStart + 4.3} />

      {/* Connector dashed lines */}
      <ConnectorLine from={[380, 400]} to={[800, 400]} delay={sceneStart + 0.3} />
      <ConnectorLine from={[920, 400]} to={[1395, 400]} delay={sceneStart + 2.8} />
    </div>
  );
}

function ColLabel({ x, y, delay, text }) {
  const t = useTime();
  const rel = t - delay;
  const opacity = rel < 0 ? 0 : Math.min(1, rel / 0.4);
  const ty = rel < 0 ? 10 : Math.max(0, 10 - (rel / 0.4) * 10);
  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      opacity, transform: `translateY(${ty}px)`,
      fontFamily: 'Onest, system-ui, sans-serif',
      fontSize: 13, letterSpacing: '.18em', textTransform: 'uppercase',
      color: BRAND.muted, fontWeight: 500,
    }}>{text}</div>
  );
}

function ConnectorLine({ from, to, delay }) {
  const t = useTime();
  const rel = t - delay;
  const p = rel < 0 ? 0 : Math.min(1, rel / 0.6);
  const eased = Easing.easeOutCubic(p);
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const len = Math.sqrt(dx * dx + dy * dy);
  const ang = Math.atan2(dy, dx) * 180 / Math.PI;
  return (
    <div style={{
      position: 'absolute',
      left: from[0], top: from[1],
      width: len * eased, height: 2,
      transform: `rotate(${ang}deg)`,
      transformOrigin: '0 50%',
      background: `repeating-linear-gradient(90deg, ${BRAND.accent} 0 6px, transparent 6px 12px)`,
      opacity: 0.5,
    }}/>
  );
}

function ClementineEngine({ x, y, delay }) {
  const t = useTime();
  const rel = t - delay;
  if (rel < -0.1) return null;
  const entryT = Math.min(1, Math.max(0, rel / 0.6));
  const scale = Easing.easeOutBack(entryT);

  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      transform: `translate(-50%, -50%) scale(${scale})`,
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14,
    }}>
      <div style={{ position: 'relative' }}>
        <ClementineMark size={180} rotation={0} />
      </div>
      <div style={{
        fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
        fontSize: 26, fontWeight: 500, letterSpacing: '-.01em',
        color: BRAND.paper, textAlign: 'center',
        opacity: entryT,
      }}>
        Clementine Analytics
      </div>
      <div style={{
        display: 'flex', gap: 8,
        opacity: Math.min(1, Math.max(0, (rel - 0.4) / 0.5)),
      }}>
        {['Hämtar', 'Strukturerar', 'Modellerar'].map(w => (
          <span key={w} style={{
            fontFamily: 'Onest, system-ui, sans-serif',
            fontSize: 12, letterSpacing: '.08em',
            color: BRAND.accentSoft,
            padding: '4px 10px',
            background: `${BRAND.accent}22`,
            border: `1px solid ${BRAND.accent}55`,
            borderRadius: 999,
          }}>{w}</span>
        ))}
      </div>
    </div>
  );
}

function SceneOutro() {
  // 12 - 15s
  return (
    <Sprite start={12} end={15}>
      {({ localTime, duration }) => {
        const t1 = Math.min(1, localTime / 0.6);
        const t2 = Math.min(1, Math.max(0, localTime - 0.4) / 0.6);
        const t3 = Math.min(1, Math.max(0, localTime - 0.8) / 0.6);
        const ctaT = Math.min(1, Math.max(0, (localTime - 2.0) / 0.5));

        return (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            gap: 32,
          }}>
            <div style={{
              display: 'flex', gap: 40, alignItems: 'flex-start', justifyContent: 'center',
              flexWrap: 'nowrap',
            }}>
              <Stat n="~3" label="DAGAR" delay={0} t={t1} />
              <Stat n="0 kr" label="STARTAVGIFT" delay={0} t={t2} />
              <Stat n="5+" label="RAPPORTER" delay={0} t={t3} />
            </div>
            <div style={{
              fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
              fontSize: 48, fontWeight: 400, fontStyle: 'italic',
              letterSpacing: '-.02em',
              color: BRAND.paper,
              textAlign: 'center',
              opacity: Math.min(1, Math.max(0, (localTime - 1.2) / 0.6)),
            }}>
              Färdigt. <span style={{ color: BRAND.accent, fontStyle: 'normal' }}>Från dag ett.</span>
            </div>
            {/* CTA link — placeholder href */}
            <a
              href="https://www.numberskills.se/produktlosning"
              target="_top"
              rel="noopener"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 14,
                padding: '18px 32px',
                background: BRAND.accent,
                color: '#fff',
                fontFamily: 'Onest, system-ui, sans-serif',
                fontSize: 22, fontWeight: 600,
                letterSpacing: '-.005em',
                borderRadius: 999,
                textDecoration: 'none',
                boxShadow: `0 14px 34px ${BRAND.accent}55, 0 2px 6px rgba(0,0,0,.3)`,
                opacity: ctaT,
                transform: `translateY(${(1 - ctaT) * 18}px) scale(${0.94 + ctaT * 0.06})`,
                cursor: 'pointer',
                transition: 'transform .2s ease, box-shadow .2s ease, background .2s ease',
                pointerEvents: ctaT > 0.5 ? 'auto' : 'none',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = BRAND.accentDeep;
                e.currentTarget.style.transform = `translateY(-2px) scale(1.02)`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = BRAND.accent;
                e.currentTarget.style.transform = `translateY(0) scale(1)`;
              }}
            >
              Kom igång med Clementine Analytics
              <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M13 5l7 7-7 7"/>
              </svg>
            </a>
            {/* Logo */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 16,
              marginTop: 12,
              opacity: Math.min(1, Math.max(0, (localTime - 1.6) / 0.5)),
            }}>
              <ClementineMark size={48} />
              <div style={{
                fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
                fontSize: 24, fontWeight: 600, letterSpacing: '-.015em',
                color: BRAND.paper, lineHeight: 1.02,
              }}>
                Clementine<br/>
                <span style={{ fontWeight: 400, color: 'rgba(251,247,241,.7)' }}>Analytics</span>
              </div>
            </div>
          </div>
        );
      }}
    </Sprite>
  );
}

function Stat({ n, label, t }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      gap: 8, minWidth: 260, whiteSpace: 'nowrap',
      opacity: t, transform: `translateY(${(1 - t) * 20}px) scale(${0.9 + t * 0.1})`,
    }}>
      <div style={{
        fontFamily: 'Bricolage Grotesque, system-ui, sans-serif',
        fontSize: 96, fontWeight: 500, letterSpacing: '-.03em',
        color: BRAND.accent, lineHeight: 1,
      }}>{n}</div>
      <div style={{
        fontFamily: 'Onest, system-ui, sans-serif',
        fontSize: 14, letterSpacing: '.18em',
        color: BRAND.muted, fontWeight: 500,
      }}>{label}</div>
    </div>
  );
}

// Background — subtle clementine watermark
function Backdrop() {
  const t = useTime();
  const drift = Math.sin(t * 0.3) * 10;
  return (
    <>
      <div style={{
        position: 'absolute', right: -180 + drift, bottom: -220,
        opacity: 0.06,
      }}>
        <ClementineMark size={700} rotation={-12 + drift * 0.5} />
      </div>
      <div style={{
        position: 'absolute', left: -120 - drift, top: -160,
        opacity: 0.04,
      }}>
        <ClementineMark size={400} rotation={40 - drift * 0.3} />
      </div>
    </>
  );
}

// Label at root for comments
function TimeLabel() {
  const t = useTime();
  React.useEffect(() => {
    const root = document.querySelector('[data-video-root]');
    if (root) root.setAttribute('data-screen-label', `t=${t.toFixed(1)}s`);
  }, [Math.floor(t)]);
  return null;
}

function ClementineVideo() {
  return (
    <div data-video-root style={{ position: 'absolute', inset: 0 }}>
      <Backdrop />
      <TimeLabel />
      <SceneIntro />
      <SceneProcess />
      <SceneOutro />
      <PlayPauseButton />
    </div>
  );
}

// Small floating play/pause control — bottom-right of the video stage.
// Uses the Timeline context exposed by Stage. When playback has reached the
// end (paused at duration), clicking restarts from t=0.
function PlayPauseButton() {
  const { playing, setPlaying, setTime, time, duration } = useTimeline();
  const isEnded = !playing && time >= duration - 0.01;

  const handle = () => {
    if (isEnded) {
      setTime(0);
      setPlaying(true);
    } else {
      setPlaying(p => !p);
    }
  };

  return (
    <button
      onClick={handle}
      aria-label={playing ? 'Pausa' : (isEnded ? 'Spela igen' : 'Spela')}
      style={{
        position: 'absolute',
        right: 28, bottom: 28,
        width: 56, height: 56,
        borderRadius: '50%',
        border: '1px solid rgba(251,247,241,.18)',
        background: 'rgba(11,11,16,.55)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        color: BRAND.paper,
        cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 6px 18px rgba(0,0,0,.35)',
        transition: 'background .18s ease, transform .18s ease, border-color .18s ease',
        padding: 0,
        zIndex: 10,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = BRAND.accent;
        e.currentTarget.style.borderColor = BRAND.accent;
        e.currentTarget.style.transform = 'scale(1.06)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(11,11,16,.55)';
        e.currentTarget.style.borderColor = 'rgba(251,247,241,.18)';
        e.currentTarget.style.transform = 'scale(1)';
      }}
    >
      {playing ? (
        // Pause icon
        <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor">
          <rect x="3"  y="2" width="4" height="14" rx="1"/>
          <rect x="11" y="2" width="4" height="14" rx="1"/>
        </svg>
      ) : isEnded ? (
        // Restart icon
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 12a9 9 0 1 0 3-6.7"/>
          <polyline points="3 4 3 9 8 9"/>
        </svg>
      ) : (
        // Play icon
        <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor">
          <path d="M5 3 L15 9 L5 15 Z"/>
        </svg>
      )}
    </button>
  );
}

Object.assign(window, { ClementineVideo, ClementineMark, BRAND });
