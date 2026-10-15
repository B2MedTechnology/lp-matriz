/* ════════════════════════════════════════════════════════════════
   Clínica de Olhos Aurora — comportamento da página
   Base: o pagina.js da página do Dr. Anselmo Rubim (a da cena rolada), sem o traçado do Doppler e sem o
   vídeo em laço, que eram dele. O evento da capa (a névoa e o feixe) é 100% CSS.
   Sem framework, sem build. Tudo defensivo: se um bloco falhar, os outros seguem, e o href real do
   WhatsApp está escrito no HTML — se este script inteiro morrer, a conversão continua.
   ════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var d = document;
  var reduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── três tempos de carga (PageSpeed) ──
     depoisDoQuadro: lê medidas SÓ depois que o navegador montou a tela (ler no meio do script é layout
     forçado — erro 12d). quandoPerto: o que é de outra dobra (API das avaliações, mapa) só carrega perto
     dela, com rede de segurança pela ROLAGEM, nunca por cronômetro (erro 12e). aoPrimeiroGesto: o pesado
     que só serve a quem mexe (os quadros da cena) espera o 1º gesto. */
  function depoisDoQuadro(fn) {
    requestAnimationFrame(function () { setTimeout(fn, 0); });
  }
  function quandoPerto(el, margem, fn) {
    if (!el) return;
    var feito = false, pend = false, obs = null;
    function vai() {
      if (feito) return;
      feito = true;
      if (obs) obs.disconnect();
      window.removeEventListener('scroll', olha);
      fn();
    }
    function olha() {
      if (feito || pend) return;
      pend = true;
      requestAnimationFrame(function () {
        pend = false;
        if (el.getBoundingClientRect().top < window.innerHeight + margem) vai();
      });
    }
    if ('IntersectionObserver' in window) {
      obs = new IntersectionObserver(function (es) { if (es[0].isIntersecting) vai(); },
                                     { rootMargin: margem + 'px 0px' });
      obs.observe(el);
    }
    window.addEventListener('scroll', olha, { passive: true });
  }
  function aoPrimeiroGesto(fn, esperaPosLoad) {
    var feito = false, evs = ['scroll', 'wheel', 'touchstart', 'pointerdown', 'keydown'];
    function vai() {
      if (feito) return;
      feito = true;
      evs.forEach(function (ev) { window.removeEventListener(ev, vai); });
      fn();
    }
    evs.forEach(function (ev) { window.addEventListener(ev, vai, { passive: true }); });
    if (d.readyState === 'complete') setTimeout(vai, esperaPosLoad);
    else window.addEventListener('load', function () { setTimeout(vai, esperaPosLoad); });
  }

  /* ── medição: só o dataLayer. Quem manda para GA4 e Meta é o GTM (quando entrar); chamar gtag()/fbq()
     daqui duplicaria o que o contêiner já manda (erro F3). ── */
  function medir(nome, dados) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push(Object.assign({ event: nome }, dados || {}));
    } catch (e) {}
  }

  d.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[data-origem],a[data-ir]');
    if (!a) return;
    if (a.hasAttribute('data-origem')) medir('agendar_click', { origem: a.getAttribute('data-origem') });
    else medir('clique_saida', { destino: a.getAttribute('data-ir') });
  });

  /* ── proteção contra o reescritor de links de rastreio (tag de WhatsApp da Comunidade NOD, comum nos
     contêineres da casa): ele cola ?utm_source= em todo link — num tel: e numa âncora, isso quebra o
     "ligar" e a navegação (erro F2). Guardamos o href original e desfazemos a reescrita na hora. ── */
  var protegidos = [].slice.call(d.querySelectorAll('a[href^="tel:"], a[href^="#"], a[href^="mailto:"]'));
  if (protegidos.length && 'MutationObserver' in window) {
    protegidos.forEach(function (a) { a._hrefOriginal = a.getAttribute('href'); });
    new MutationObserver(function (ms) {
      ms.forEach(function (m) {
        var a = m.target;
        if (a._hrefOriginal && a.getAttribute('href') !== a._hrefOriginal) a.setAttribute('href', a._hrefOriginal);
      });
    }).observe(d.body, { attributes: true, attributeFilter: ['href'], subtree: true });
  }

  /* ════════ CABEÇALHO, FLUTUANTE E BARRA — UMA conta só, num requestAnimationFrame (erro 10) ════════ */
  var topo = d.getElementById('topo');
  var flut = d.getElementById('flutuante');
  var barra = d.getElementById('barra');
  var capa = d.getElementById('capa');
  var rodape = d.querySelector('.rodape');
  var pendente = false;

  function aoRolar() {
    if (pendente) return;
    pendente = true;
    requestAnimationFrame(function () {
      pendente = false;
      var y = window.scrollY || d.documentElement.scrollTop;
      if (topo) topo.classList.toggle('compacto', y > 40);
      var passouCapa = capa ? y > capa.offsetHeight * 0.78 : y > 500;
      var sobreRodape = false;
      if (rodape) sobreRodape = rodape.getBoundingClientRect().top < window.innerHeight - 60;
      var mostrar = passouCapa && !sobreRodape;
      if (flut) flut.classList.toggle('visivel', mostrar);
      if (barra) barra.classList.toggle('visivel', mostrar);
    });
  }
  window.addEventListener('scroll', aoRolar, { passive: true });
  window.addEventListener('resize', aoRolar);
  aoRolar();

  /* ════════ 1 · O EVENTO DA CAPA — só para de gastar quadro quando a dobra SAI DA TELA ════════
     A névoa e o feixe são CSS; aqui só a pausa. ⚠️ Nunca pausar no hover. */
  if (capa && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      capa.classList.toggle('capa--parado', !es[0].isIntersecting);
    }, { threshold: 0 }).observe(capa);
  }

  /* ════════ 1b · CAPA EM VÍDEO EM LAÇO — a variação da página da Dra. Heloísa Figueiral (o bloco do Dr. Anselmo Rubim) ════════
     O último quadro (o close no aparelho) e o primeiro (a consulta, plano aberto) são cenas diferentes: com o `loop` puro a
     volta corta seco a cada 8 s. Aqui a volta vira DISSOLUÇÃO entre duas cópias do mesmo arquivo (a 2ª sai do cache).
     Sem autoplay no HTML e com preload="none": o vídeo começa no 1º gesto ou 1,5 s depois do load; até lá (e sem JS)
     fica o poster, que é o mesmo quadro. */
  var filme = d.getElementById('filme');
  var v1 = d.getElementById('capa-video');
  if (filme && v1 && !reduzido) aoPrimeiroGesto(function () {
    var FUNDE = 1.1;                                   // s — igual ao transition do CSS
    v1.muted = true;                                   // a PROPRIEDADE: sem ela o iOS recusa o play()
    v1.loop = false;
    v1.preload = 'auto';
    var v2 = v1.cloneNode(false);
    v2.removeAttribute('id');
    v2.muted = true; v2.preload = 'none';
    filme.appendChild(v2);
    filme.classList.add('pronto');
    v1.addEventListener('canplaythrough', function () { v2.preload = 'auto'; v2.load(); }, { once: true });
    var ativo = v1, reserva = v2, trocando = false, naTela = true, raf = 0, voltas = 0;

    function acender() { v1.classList.add('no-ar', 'frente'); }
    v1.addEventListener('playing', acender, { once: true });

    /* 22-09 — o iPhone no Modo de Pouca Energia RECUSA todo play() que não nasça de um toque (NotAllowedError). Até aqui a
       recusa era engolida e o vídeo ficava no pôster para sempre — nem tocar na tela religava (a dona viu "travado" no celular).
       Agora a recusa ARMA uma nova tentativa no próximo toque, clique ou tecla — touchend, pointerup, click e keydown são os
       eventos que valem como ativação; touchstart e scroll NÃO valem — e o mesmo toque destrava a 2ª cópia (play + pause),
       para a volta dissolvida seguir funcionando. Teste que prova: ferramentas/medir-laco-recusado.py. */
    var armado = false, ATIVA = ['touchend', 'pointerup', 'click', 'keydown'];
    function religarNoToque() {
      if (armado) return;
      armado = true;
      function tenta() {
        armado = false;
        ATIVA.forEach(function (ev) { d.removeEventListener(ev, tenta, true); });
        if (window.__pausado) return;
        var p = ativo.play();
        if (p && p.catch) p.catch(religarNoToque);
        var r = reserva, q = r.play();
        if (q && q.then) q.then(function () { if (r !== ativo) { r.pause(); r.currentTime = 0; } }, function () {});
      }
      ATIVA.forEach(function (ev) { d.addEventListener(ev, tenta, { capture: true, passive: true }); });
    }
    var p0 = window.__pausado ? null : v1.play();      // pausado pelo botão (ou pela escolha guardada): fica no pôster
    if (p0 && p0.catch) p0.catch(religarNoToque);      // recusado: o pôster segura a dobra até o 1º toque

    function virar() {
      trocando = true;
      reserva.currentTime = 0;
      var seguir = function () {
        reserva.classList.add('frente', 'no-ar');
        ativo.classList.remove('frente');
        setTimeout(function () {
          ativo.classList.remove('no-ar');
          ativo.pause();
          var t = ativo; ativo = reserva; reserva = t;
          trocando = false;
          voltas += 1;
          if (voltas <= 3) medir('capa_video_volta', { volta: voltas });
        }, FUNDE * 1000 + 80);
      };
      var p = reserva.play();
      // se o navegador recusar a segunda cópia, volta para o laço simples
      if (p && p.then) p.then(seguir, function () { trocando = false; ativo.loop = true; ativo.play(); });
      else seguir();
    }

    function laco() {
      raf = 0;
      if (!naTela) return;
      if (!trocando && ativo.duration &&
          (ativo.ended || ativo.currentTime >= ativo.duration - FUNDE)) virar();
      raf = requestAnimationFrame(laco);
    }
    // rede de segurança: o rAF não roda em aba oculta; o 'ended' roda
    [v1, v2].forEach(function (v) {
      v.addEventListener('ended', function () { if (v === ativo && !trocando) virar(); });
    });

    // fora da tela para de decodificar (vídeo em laço gasta bateria); nunca no hover
    if (capa && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        naTela = es[0].isIntersecting;
        if (naTela) {
          if (ativo.paused && !window.__pausado) { var p = ativo.play(); if (p && p.catch) p.catch(religarNoToque); }
          if (!raf) raf = requestAnimationFrame(laco);
        } else {
          ativo.pause();
          if (raf) { cancelAnimationFrame(raf); raf = 0; }
        }
      }, { threshold: 0 }).observe(capa);
    } else raf = requestAnimationFrame(laco);
  }, 0);   // o laço começa no LOAD (era 1,5 s depois: a dona sentiu o vídeo demorar a começar, 16-09)

  /* ════════ 1c · A CENA — o vídeo que a ROLAGEM arrasta (a página da Dra. Heloísa Figueiral) ════════
     O motor da página do Dr. Anselmo Rubim, como está: 60 fps medidos, ≤ 38 quadros decodificados vivos.
     Cada posição da rolagem é um quadro; o canvas desenha a sequência AVIF com o MESMO corte do poster
     (--foco no CSS). Sem JS, com movimento reduzido ou economia de dados: o 1º quadro parado. */
  var cena = d.querySelector('[data-cena]');
  var tela = d.getElementById('cena-filme');
  if (cena && tela && tela.getContext) depoisDoQuadro(function () {
    var conexao = navigator.connection || {};
    var economia = conexao.saveData || /2g$/.test(conexao.effectiveType || '');
    var TOTAL = parseInt(tela.getAttribute('data-total'), 10) || 0;
    var molde = tela.getAttribute('data-quadros') || '';
    var moldeMovel = tela.getAttribute('data-quadros-movel') || '';
    if (reduzido || economia || !TOTAL) return;
    var caixa0 = tela.getBoundingClientRect();
    var usaMovel = !!moldeMovel && caixa0.height > 0 && caixa0.width / caixa0.height <= 1.05;
    if (usaMovel) molde = moldeMovel;
    /* DUAS telas empilhadas: a de baixo mostra o quadro da posição e a de cima o SEGUINTE, com opacidade =
       a fração que sobra. Quem mistura é o compositor: 1 desenho por quadro (erro 12c). */
    var tela2 = tela.cloneNode(false);
    [].slice.call(tela2.attributes).forEach(function (a) { if (a.name === 'id' || /^data-/.test(a.name)) tela2.removeAttribute(a.name); });
    tela2.setAttribute('aria-hidden', 'true');
    tela.parentNode.insertBefore(tela2, tela.nextSibling);
    var baixo = { el: tela, ctx: tela.getContext('2d'), mostra: -1 };
    var cima = { el: tela2, ctx: tela2.getContext('2d'), mostra: -1 };
    var opacCima = -1;
    var quadros = [], atual = 0, alvo = 0, anim = 0, dir = 1;
    var ultimoT = 0, sujo = true, dentroAntes = true;
    var W = 0, H = 0, foco = 0.4, topoCena = 0, curso = 1, vh = window.innerHeight, movel = false, linha = 0;

    function lim(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

    /* BAIXAR e DECODIFICAR são etapas separadas: todos baixados (Blob), só uma JANELA decodificada
       (ImageBitmap, fora da thread principal) — decodificados, os quadros dariam ~700 MB. */
    var FIXO = 16, blobs = [], baixado = [], baixando = [], emCurso = 0;
    // medição (ferramentas/medir-atraso-cena.py): com ?medir-cena na URL, o estado do motor fica em window.__cena
    var MEDIR_CENA = /[?&]medir-cena/.test(location.search);
    // a suavização: τ = 0,11 s no Dr. Anselmo Rubim; no página-base a dona sentiu o vídeo "com delay" atrás do dedo (16-09) — numa passada
    // de 1.500 px/s ele ficava ~20 quadros atrás. 0,04 s segue o dedo e mantém a mistura entre quadros. Com
    // ?medir-cena&tau=0.11 na URL dá para comparar (ferramentas/medir-atraso-cena.py).
    var TAU = 0.04, tauUrl = /[?&]tau=([\d.]+)/.exec(location.search);
    if (MEDIR_CENA && tauUrl) TAU = parseFloat(tauUrl[1]) || TAU;
    var quer = [], decod = [], emDecod = 0;
    var mapaOk = !!(window.createImageBitmap && window.fetch);
    function fixo(i) { return i % FIXO === 0 || i === TOTAL - 1; }
    function endereco(i) { return molde.replace('{n}', ('00' + i).slice(-3)); }
    var grossa = [0, TOTAL - 1];
    for (var passo = 64; passo >= FIXO; passo = passo >> 1)
      for (var k = 0; k < TOTAL; k += passo) if (grossa.indexOf(k) < 0) grossa.push(k);
    function proximo() {
      for (var q = 0; q < grossa.length; q++) if (!baixado[grossa[q]] && !baixando[grossa[q]]) return grossa[q];
      var c = Math.round(atual), melhor = -1, menor = Infinity;
      for (var i = 0; i < TOTAL; i++) {
        if (baixado[i] || baixando[i]) continue;
        var dd = (i - c) * dir, custo = dd >= 0 ? dd : -dd * 3;
        if (custo < menor) { menor = custo; melhor = i; }
      }
      return melhor;
    }
    function baixar() {
      for (var i; emCurso < 10 && (i = proximo()) >= 0;) buscar(i);     // 10 de uma vez (HTTP/2; eram 6)
    }
    function buscar(i) {
      baixando[i] = 1; emCurso++;
      var fim = function () { baixando[i] = 0; baixado[i] = 1; emCurso--; baixar(); pedir(); };
      if (!mapaOk) return viaImg(endereco(i), i, fim);
      fetch(endereco(i)).then(function (r) { if (!r.ok) throw r.status; return r.blob(); })
        .then(function (b) { blobs[i] = b; fim(); }, fim);
    }
    function viaImg(src, i, fim) {
      var im = new Image();
      var ok = function () { quadros[i] = im; if (src.indexOf('blob:') === 0) URL.revokeObjectURL(src); fim(); };
      im.src = src;
      if (im.decode) im.decode().then(ok, function () { if (im.complete && im.naturalWidth) ok(); else fim(); });
      else { im.onload = ok; im.onerror = fim; }
    }
    function decodificar(i) {
      decod[i] = 1; emDecod++;
      var fim = function () { decod[i] = 0; emDecod--; pedir(); };
      if (!mapaOk) return viaImg(URL.createObjectURL(blobs[i]), i, fim);
      createImageBitmap(blobs[i]).then(function (bmp) {
        if (quer[i]) quadros[i] = bmp; else bmp.close();
        fim();
      }, function () { mapaOk = false; decod[i] = 0; emDecod--; decodificar(i); });
    }
    /* A janela, refeita a cada quadro de tela: 2 = decodificar, 1 = pode ficar (folga), 0 = fechar.
       A folga vale só para a JANELA, nunca para o esqueleto (erro 12b). */
    function manter() {
      var c = Math.round(atual), a = Math.round(alvo), i, j, q;
      var marca = function (lo, hi) { for (var n = Math.max(0, lo); n <= Math.min(TOTAL - 1, hi); n++) quer[n] = 2; };
      for (i = 0; i < TOTAL; i++) quer[i] = 0;
      marca(c - 3, c + 3);
      if (a >= c) marca(c, Math.min(a, c + 24)); else marca(Math.max(a, c - 24), c);
      marca(a - 6, a + 6);
      if (dir > 0) marca(a, a + 14); else marca(a - 14, a);
      for (i = 0; i < TOTAL; i++) if (quer[i] === 2)
        for (j = Math.max(0, i - 4); j <= Math.min(TOTAL - 1, i + 4); j++) if (!quer[j]) quer[j] = 1;
      for (i = 0; i < TOTAL; i++) if (fixo(i)) quer[i] = 2;
      for (i = 0; i < TOTAL; i++)
        if (!quer[i] && quadros[i] && quadros[i].close) { quadros[i].close(); quadros[i] = null; }
      if (emDecod >= 4) return;
      var fila = [], custo = function (x) { var dd = (x - c) * dir; return dd >= 0 ? dd : 0.5 - dd; };
      for (i = 0; i < TOTAL; i++) if (quer[i] === 2 && blobs[i] && !quadros[i] && !decod[i]) fila.push(i);
      fila.sort(function (x, y) { return custo(x) - custo(y); });
      for (q = 0; q < fila.length && emDecod < 4; q++) decodificar(fila[q]);
    }
    function maisPerto(i) {
      if (quadros[i]) return i;
      for (var k = 1; k < TOTAL; k++) {
        if (quadros[i - k]) return i - k;
        if (quadros[i + k]) return i + k;
      }
      return -1;
    }
    function pinta(c, i) {
      var im = quadros[i], iw = im.naturalWidth || im.width, ih = im.naturalHeight || im.height;
      var esc = Math.max(W / iw, H / ih), dw = iw * esc, dh = ih * esc;
      c.ctx.drawImage(im, (W - dw) * foco, (H - dh) / 2, dw, dh);
      c.mostra = i;
    }
    function desenhar() {
      if (!W || !H) return;
      var i0 = Math.floor(atual), f = atual - i0, i1 = Math.min(TOTAL - 1, i0 + 1);
      var a = quadros[i0] ? i0 : maisPerto(Math.round(atual));
      if (a < 0) return;
      if (baixo.mostra !== a) {
        if (cima.mostra === a || baixo.mostra === i1) { var t = baixo; baixo = cima; cima = t; }
        if (baixo.mostra !== a) pinta(baixo, a);
        baixo.el.style.zIndex = '2'; baixo.el.style.opacity = '1';
        cima.el.style.zIndex = '3'; opacCima = -1;
      }
      var o = (a === i0 && i1 !== i0 && quadros[i1] && f > 0.005) ? Math.round(f * 1000) / 1000 : 0;
      if (o && cima.mostra !== i1) pinta(cima, i1);
      if (o !== opacCima) { cima.el.style.opacity = String(o); opacCima = o; }
    }

    function palavras(el) {
      if (el.hasAttribute('data-pl')) return [].slice.call(el.querySelectorAll('.pl'));
      el.setAttribute('data-pl', '');
      var n = 0;
      (function andar(no) {
        [].slice.call(no.childNodes).forEach(function (f) {
          if (f.nodeType === 3) {
            var frag = d.createDocumentFragment();
            f.textContent.split(/(\s+)/).forEach(function (p) {
              if (!p) return;
              if (/^\s+$/.test(p)) { frag.appendChild(d.createTextNode(p)); return; }
              var s = d.createElement('span');
              s.className = 'pl'; s.textContent = p; s.style.setProperty('--i', n++);
              frag.appendChild(s);
            });
            no.replaceChild(frag, f);
          } else if (f.nodeType === 1 && f.tagName !== 'BR') andar(f);
        });
      })(el);
      return [].slice.call(el.querySelectorAll('.pl'));
    }
    var h1 = cena.querySelector('.cena__bloco--capa h1');
    if (h1) palavras(h1);
    var h2 = cena.querySelector('.cena__bloco--quem h2');
    var h2pl = h2 ? palavras(h2) : [];
    var capaTxt = [].slice.call(cena.querySelectorAll('.cena__bloco--capa .capa__env > *'));
    var quemTxt = [].slice.call(cena.querySelectorAll('.cena__bloco--quem .quem__texto > *'))
      .filter(function (el) { return el.tagName !== 'UL' && el.tagName !== 'OL'; })
      .concat([].slice.call(cena.querySelectorAll('.cena__bloco--quem .motivos li')));
    var ultimoR = -1, mexeu = false;

    /* O texto se dissolve numa LINHA FIXA da tela ao subir — por MÁSCARA, não por opacidade. */
    function saida(el, r) {
      var rampa = 56;
      if (r.bottom <= linha - rampa / 2) { limpa(el); return 0; }
      if (r.top >= linha + rampa / 2) { limpa(el); return 1; }
      var x = Math.round(linha - r.top);
      var m = 'linear-gradient(to bottom, transparent ' + (x - rampa / 2) + 'px, #000 ' + (x + rampa / 2) + 'px)';
      el.style.webkitMaskImage = m; el.style.maskImage = m; el._mascara = true;
      return 1;
    }
    function limpa(el) {
      if (el._mascara) { el.style.webkitMaskImage = ''; el.style.maskImage = ''; el._mascara = false; }
    }
    function textos() {
      var rc = capaTxt.map(function (el) { return el.getBoundingClientRect(); });
      var rq = quemTxt.map(function (el) { return el.getBoundingClientRect(); });
      var rh = h2 ? h2.getBoundingClientRect() : null;
      capaTxt.forEach(function (el, k) { el.style.opacity = saida(el, rc[k]) ? '' : '0'; });
      quemTxt.forEach(function (el, k) {
        var r = rq[k], fica = saida(el, r);
        if (el === h2) { el.style.opacity = fica ? '' : '0'; return; }
        var entra = lim((vh * 0.98 - r.top) / (vh * 0.14));
        el.style.opacity = (entra * fica).toFixed(3);
        el.style.transform = 'translate3d(0,' + ((1 - entra) * 22).toFixed(1) + 'px,0)';
        if (el.tagName === 'LI') el.style.setProperty('--e', entra.toFixed(3));
      });
      if (rh && mexeu) {
        var r = lim((vh * 0.9 - rh.top) / (vh * 0.45));
        if (Math.abs(r - ultimoR) > 0.002) {
          ultimoR = r;
          var n = h2pl.length;
          h2pl.forEach(function (s, i) { s.style.opacity = (0.16 + 0.84 * lim(r * n - i)).toFixed(3); });
        }
      }
    }

    function geometria() {
      vh = window.innerHeight; movel = window.innerWidth <= 900;
      var r = tela.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 3);
      var w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
      if (w && h && (w !== W || h !== H)) {
        W = w; H = h;
        [baixo, cima].forEach(function (c) {
          c.el.width = w; c.el.height = h; c.mostra = -1;
          c.ctx.imageSmoothingEnabled = true; c.ctx.imageSmoothingQuality = 'high';
        });
      }
      foco = usaMovel ? 0.5 : (parseFloat(getComputedStyle(tela).getPropertyValue('--foco')) || 0.4);
      topoCena = cena.getBoundingClientRect().top + (window.scrollY || d.documentElement.scrollTop);
      curso = Math.max(1, cena.offsetHeight - vh);
      var et = cena.querySelector('.cena__bloco--capa .capa__env > *');
      var repouso = et ? et.getBoundingClientRect().top + (window.scrollY || d.documentElement.scrollTop) - topoCena : vh;
      linha = movel ? Math.min(vh * 0.40, repouso - 8) : vh * 0.12;
    }
    var marcou = {};
    function rolou() {
      var y = window.scrollY || d.documentElement.scrollTop;
      var dentro = y < topoCena + curso + vh * 1.5;
      if (!dentro && !dentroAntes) return;
      dentroAntes = dentro;
      var p = lim((y - topoCena) / curso), novo = p * (TOTAL - 1);
      if (novo !== alvo) dir = novo > alvo ? 1 : -1;
      alvo = novo;
      [50, 100].forEach(function (m) {
        if (!marcou[m] && p >= m / 100 - 0.02) { marcou[m] = true; medir('cena_video', { marco: m }); }
      });
      sujo = true;
      pedir();
    }
    function pedir() { if (!anim) anim = requestAnimationFrame(quadro); }
    function quadro(t) {
      anim = 0;
      var dt = ultimoT ? Math.min(0.1, (t - ultimoT) / 1000) : 1 / 60;
      ultimoT = t;
      atual += (alvo - atual) * (1 - Math.exp(-dt / TAU));        // suavização pelo TEMPO (τ = TAU, 0,04 s)
      if (Math.abs(alvo - atual) < 0.01) atual = alvo;
      manter();
      desenhar();
      if (MEDIR_CENA) window.__cena = { alvo: alvo, atual: atual, mostra: baixo.mostra, baixados: blobs.filter(Boolean).length };
      if (sujo) { sujo = false; textos(); }
      if (atual !== alvo) pedir(); else ultimoT = 0;
    }
    function refaz() { geometria(); rolou(); }
    geometria();
    // os quadros começam no LOAD (eram 2,5 s depois): o poster já pintou, então não disputam o LCP (16-09)
    aoPrimeiroGesto(baixar, 0);
    rolou();
    window.addEventListener('scroll', function () { mexeu = true; rolou(); }, { passive: true });
    window.addEventListener('resize', refaz);
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(refaz);
    if ('ResizeObserver' in window) new ResizeObserver(refaz).observe(cena);
  });

  /* ════════ MANCHETES — palavra por palavra, em TODAS as dobras ════════
     O h1 da capa acende no carregamento (CSS); cada h2 acende conforme sobe na tela. Nada apaga antes da
     1ª rolagem (erro 12f): na 1ª, o título que JÁ está na tela fica aceso de vez. */
  (function () {
    if (reduzido) return;
    function quebra(el) {
      if (el.hasAttribute('data-pl')) return null;
      el.setAttribute('data-pl', '');
      var n = 0;
      (function andar(no) {
        [].slice.call(no.childNodes).forEach(function (f) {
          if (f.nodeType === 3) {
            var frag = d.createDocumentFragment();
            f.textContent.split(/(\s+)/).forEach(function (p) {
              if (!p) return;
              if (/^\s+$/.test(p)) { frag.appendChild(d.createTextNode(p)); return; }
              var s = d.createElement('span');
              s.className = 'pl'; s.textContent = p; s.style.setProperty('--i', n++);
              frag.appendChild(s);
            });
            no.replaceChild(frag, f);
          } else if (f.nodeType === 1 && f.tagName !== 'BR') andar(f);
        });
      })(el);
      return [].slice.call(el.querySelectorAll('.pl'));
    }
    var h1 = d.querySelector('.capa h1');
    if (h1) quebra(h1);
    var mans = [].slice.call(d.querySelectorAll('main h2')).map(function (h) {
      var pl = h.closest('[data-cena]') ? null : quebra(h); return pl ? { h: h, pl: pl, r: -1 } : null;
    }).filter(Boolean);
    if (!mans.length) return;
    var pend = false, armado = false;
    function pinta() {
      pend = false;
      var vh = window.innerHeight;
      var tops = mans.map(function (m) { return m.h.getBoundingClientRect().top; });
      if (!armado) {
        armado = true;
        var ficam = [], seus = [];
        mans.forEach(function (m, k) { if (tops[k] >= vh) { ficam.push(m); seus.push(tops[k]); } });
        mans = ficam; tops = seus;
      }
      mans.forEach(function (m, k) {
        var r = Math.max(0, Math.min(1, (vh * 0.92 - tops[k]) / (vh * 0.42)));
        if (Math.abs(r - m.r) < 0.002) return;
        m.r = r;
        var n = m.pl.length;
        m.pl.forEach(function (s, i) { s.style.opacity = (0.16 + 0.84 * Math.max(0, Math.min(1, r * n - i))).toFixed(3); });
      });
    }
    function pede() { if (!pend) { pend = true; requestAnimationFrame(pinta); } }
    window.addEventListener('scroll', pede, { passive: true });
    window.addEventListener('resize', function () { if (armado) pede(); });
  })();

  /* ════════ 3, 4 e 4b · ENTRADAS — os motivos, os cards e os médicos entram em sequência ════════
     Pela ROLAGEM, não por IntersectionObserver (erro 11). Mede ANTES de pôr o .vivo e marca na mesma
     passada o que já está na tela: nenhum card visível pisca apagado. Sem JS, tudo visível. */
  [].forEach.call(d.querySelectorAll('[data-entra]'), function (sec) {
    var itens = [].slice.call(sec.querySelectorAll('.cards li, .medicos li, .motivos li'));
    if (!itens.length || reduzido) return;
    var checa = function () {
      var vh = window.innerHeight;
      var tops = itens.map(function (li) { return li.classList.contains('dentro') ? null : li.getBoundingClientRect().top; });
      itens.forEach(function (li, k) { if (tops[k] !== null && tops[k] < vh * 0.9) li.classList.add('dentro'); });
    };
    depoisDoQuadro(function () {
      var vh = window.innerHeight;
      var tops = itens.map(function (li) { return li.getBoundingClientRect().top; });
      sec.classList.add('vivo');
      itens.forEach(function (li, k) { if (tops[k] < vh * 0.9) li.classList.add('dentro'); });
      window.addEventListener('scroll', checa, { passive: true });
      window.addEventListener('resize', checa);
    });
  });

  /* ════════ 2 · NÚMEROS — contagem ao entrar na tela ════════
     A rede de segurança compara com o VALOR FINAL, não com o vazio (erro 11a). */
  var contadores = [].slice.call(d.querySelectorAll('[data-conta]'));
  function contar(el) {
    var alvo = el.getAttribute('data-conta');
    var num = parseFloat(alvo.replace(',', '.'));
    if (isNaN(num) || reduzido) { el.textContent = alvo; return; }
    var casas = alvo.indexOf(',') > -1 ? 1 : 0;
    var t0 = performance.now(), dur = 1400;
    (function passo(t) {
      var p = Math.max(0, Math.min(1, (t - t0) / dur));
      var v = num * (1 - Math.pow(1 - p, 3));
      el.textContent = casas ? v.toFixed(1).replace('.', ',') : Math.round(v).toLocaleString('pt-BR');
      if (p < 1) requestAnimationFrame(passo); else el.textContent = alvo;
    })(t0);
  }
  if (contadores.length) {
    if ('IntersectionObserver' in window) {
      var oc = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (en.isIntersecting) { contar(en.target); oc.unobserve(en.target); }
        });
      }, { threshold: .4 });
      contadores.forEach(function (el) { oc.observe(el); });
    }
    setTimeout(function () {
      contadores.forEach(function (el) {
        if (el.textContent !== el.getAttribute('data-conta')) el.textContent = el.getAttribute('data-conta');
      });
    }, 3200);
  }

  /* A FAIXA: duas condições para o laço (erro 9b) — a METADE do trilho cobre a vitrine e o trilho são
     duas metades iguais. Velocidade constante de 38 px/s. */
  var trilhoN = d.querySelector('.numeros__lista');
  if (trilhoN && !reduzido) {
    var montaFaixa = function () {
      var itens = [].slice.call(trilhoN.children), k = itens.length / 2, metade = 0;
      for (var i = 0; i < k; i++) metade += itens[i].getBoundingClientRect().width;
      var vit = trilhoN.parentNode.getBoundingClientRect().width;
      if (metade && metade < vit * 1.05) {
        var copias = itens.slice(k), vezes = Math.ceil((vit * 1.05) / metade) - 1;
        for (var v = 0; v < vezes; v++) {
          copias.forEach(function (c) { trilhoN.insertBefore(c.cloneNode(true), itens[k]); });
          copias.forEach(function (c) { trilhoN.appendChild(c.cloneNode(true)); });
        }
        metade *= (vezes + 1);
      }
      if (metade) trilhoN.style.setProperty('--dur', Math.max(24, metade / 38).toFixed(1) + 's');
    };
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(function () { depoisDoQuadro(montaFaixa); });
    else depoisDoQuadro(montaFaixa);
  }

  /* ════════ 5 · PASSOS — a linha do tempo acompanha a rolagem (régua a 60% da tela) ════════
     O .vivo só entra na 1ª rolagem: antes dela, quem não rola lê tudo com contraste cheio. */
  var listaPassos = d.querySelector('.passos');
  var passos = listaPassos ? [].slice.call(listaPassos.children) : [];
  if (passos.length && !reduzido) {
    var pendP = false;
    var pintaPassos = function () {
      pendP = false;
      var vh = window.innerHeight, r = listaPassos.getBoundingClientRect(), linha = vh * 0.6;
      var tops = passos.map(function (li) { return li.getBoundingClientRect().top; });
      listaPassos.style.setProperty('--prog', Math.max(0, Math.min(1, (linha - r.top) / r.height)).toFixed(4));
      var atual = -1;
      passos.forEach(function (li, i) {
        var passou = tops[i] < linha;
        li.classList.toggle('passou', passou);
        if (passou) atual = i;
      });
      passos.forEach(function (li, i) { li.classList.toggle('atual', i === atual); });
    };
    var armouP = false;
    var pedeP = function () {
      if (!armouP) { armouP = true; listaPassos.classList.add('vivo'); }
      if (!pendP) { pendP = true; requestAnimationFrame(pintaPassos); }
    };
    window.addEventListener('scroll', pedeP, { passive: true });
    window.addEventListener('resize', function () { if (armouP) pedeP(); });
  }

  /* ════════ 6 · A FAIXA DO ESPAÇO — laço contínuo (4ª rodada) ════════
     A mecânica da faixa dos números: a lista sai duplicada do gerar.py, o JS repete as metades até cobrir a vitrine
     (erro 9b) e acerta a velocidade em px/s. Fora da tela, para. */
  var trilhoS = d.querySelector('.carrossel__trilho');
  if (trilhoS && !reduzido) {
    var montaSala = function () {
      var itens = [].slice.call(trilhoS.children), k = itens.length / 2, metade = 0;
      for (var i = 0; i < k; i++) metade += itens[i].getBoundingClientRect().width;
      var vit = trilhoS.parentNode.getBoundingClientRect().width;
      if (metade && metade < vit * 1.05) {
        var copias = itens.slice(k), vezes = Math.ceil((vit * 1.05) / metade) - 1;
        for (var v = 0; v < vezes; v++) {
          copias.forEach(function (c) { trilhoS.insertBefore(c.cloneNode(true), itens[k]); });
          copias.forEach(function (c) { trilhoS.appendChild(c.cloneNode(true)); });
        }
        metade *= (vezes + 1);
      }
      if (metade) trilhoS.style.setProperty('--dur', Math.max(30, metade / 28).toFixed(1) + 's');
    };
    depoisDoQuadro(montaSala);
    var salaSec = d.getElementById('sala');
    if ('IntersectionObserver' in window && salaSec) {
      new IntersectionObserver(function (es) { salaSec.classList.toggle('sala--parada', !es[0].isIntersecting); }).observe(salaSec);
    }
  }

  /* ════════ 7 · AVALIAÇÕES DO GOOGLE ════════
     A dobra nasce CHEIA com a semente e a API SOMA — não substitui (a Places devolve no máximo 5 e quem
     escolhe é o Google). Depois de somar, REORDENA por data. */
  var secProva = d.getElementById('avaliacoes');
  var trilho = d.getElementById('prova-trilho');
  var lista = [];

  function texto(t) { return (t == null ? '' : String(t)); }

  function estrelas(n) {
    var s = '';
    for (var i = 0; i < 5; i++) s += '<svg width="13" height="13" aria-hidden="true"><use href="#ico-estrela"></use></svg>';
    // role="img": aria-label num <span> sem papel é atributo PROIBIDO (erro 12g)
    return '<span class="depos__estrelas" role="img" aria-label="' + (n || 5) + ' de 5 estrelas">' + s + '</span>';
  }

  function cartao(a) {
    var li = d.createElement('article');
    li.className = 'depos';
    var cab = d.createElement('div'); cab.className = 'depos__topo';
    var ini = (texto(a.nome).trim()[0] || '?').toUpperCase();
    if (a.foto) {
      var img = d.createElement('img');
      // ⚠️ loading e referrerpolicy ANTES do src: depois não valem
      img.loading = 'lazy';
      img.referrerPolicy = 'no-referrer';
      img.className = 'depos__foto';
      img.width = 38; img.height = 38; img.alt = '';
      img.onerror = function () {
        var s = d.createElement('span');
        s.className = 'depos__foto depos__foto--vazia';
        s.textContent = ini;
        img.replaceWith(s);
      };
      img.src = a.foto;
      cab.appendChild(img);
    } else {
      var s = d.createElement('span');
      s.className = 'depos__foto depos__foto--vazia';
      s.textContent = ini;
      cab.appendChild(s);
    }
    var quem = d.createElement('div');
    var nome = d.createElement('div'); nome.className = 'depos__nome';
    nome.textContent = texto(a.nome);                 // textContent, NUNCA innerHTML: conteúdo de terceiro
    var quando = d.createElement('div'); quando.className = 'depos__quando';
    quando.textContent = texto(a.quando);
    quem.appendChild(nome); quem.appendChild(quando);
    cab.appendChild(quem);
    li.appendChild(cab);
    li.insertAdjacentHTML('beforeend', estrelas(a.nota));
    var p = d.createElement('p'); p.className = 'depos__texto';
    p.textContent = texto(a.texto);
    li.appendChild(p);
    if (a.link) {
      var l = d.createElement('a');
      l.className = 'depos__link'; l.href = a.link;
      l.target = '_blank'; l.rel = 'noopener nofollow';
      l.textContent = 'Ver no Google';
      li.appendChild(l);
    }
    return li;
  }

  function pintar() {
    if (!trilho) return;
    trilho.textContent = '';
    lista.forEach(function (a) { trilho.appendChild(cartao(a)); });
    depoisDoQuadro(posicao);
  }

  function chave(a) {
    return (texto(a.nome).trim().toLowerCase() + '|' + texto(a.texto).trim().slice(0, 40).toLowerCase());
  }

  try {
    var semente = d.getElementById('prova-semente');
    if (semente) lista = JSON.parse(semente.textContent) || [];
  } catch (e) { lista = []; }
  pintar();

  if (secProva && secProva.getAttribute('data-avaliacoes')) quandoPerto(secProva, 1500, function () {
    fetch(secProva.getAttribute('data-avaliacoes'), { headers: { accept: 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.ok) return;
        var m = d.getElementById('prova-media'), t = d.getElementById('prova-total');
        if (m && j.media) m.textContent = Number(j.media).toFixed(1).replace('.', ',');
        if (t && j.total) t.textContent = String(j.total);
        var tenho = {};
        lista.forEach(function (a) { tenho[chave(a)] = 1; });
        var novas = (j.avaliacoes || []).filter(function (a) { return !tenho[chave(a)]; });
        if (!novas.length) return;
        lista = novas.concat(lista).sort(function (a, b) {
          var da = a.data || '', db = b.data || '';
          if (!da && !db) return 0;
          if (!da) return 1;
          if (!db) return -1;
          return db < da ? -1 : db > da ? 1 : 0;
        });
        pintar();
      })
      .catch(function () { /* sem rede: vale a semente */ });
  });

  /* carrossel automático: anda por ÍNDICE (somar ao scrollLeft dá passos desiguais) */
  var iProva = 0, pausaAte = 0, timerProva = null;
  function posicao() {
    var b = d.getElementById('prova-pos');
    if (!b || !trilho || !trilho.scrollWidth) return;
    var frac = trilho.clientWidth / trilho.scrollWidth;
    var andado = trilho.scrollLeft / Math.max(1, trilho.scrollWidth - trilho.clientWidth);
    b.style.width = Math.max(8, frac * 100) + '%';
    b.style.transform = 'translateX(' + (andado * (100 / Math.max(frac, .01) - 100)) + '%)';
  }
  function andarProva() {
    if (!trilho || window.__pausado || Date.now() < pausaAte) return;   // o botão de pausa para o carrossel também (WCAG 2.2.2)
    var cards = trilho.querySelectorAll('.depos');
    if (cards.length < 2) return;
    iProva = (iProva + 1) % cards.length;
    if (iProva === 0) trilho.scrollTo({ left: 0, behavior: 'smooth' });
    else trilho.scrollTo({ left: cards[iProva].offsetLeft - trilho.offsetLeft, behavior: 'smooth' });
  }
  if (trilho) {
    trilho.addEventListener('scroll', posicao, { passive: true });
    ['pointerdown', 'touchstart', 'wheel'].forEach(function (ev) {
      trilho.addEventListener(ev, function () { pausaAte = Date.now() + 9000; }, { passive: true });
    });
    if ('IntersectionObserver' in window && !reduzido) {
      new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) {
          if (!timerProva) timerProva = setInterval(andarProva, 5000);
          if (!secProva.dataset.medido) { secProva.dataset.medido = '1'; medir('avaliacoes_google', {}); }
        } else if (timerProva) { clearInterval(timerProva); timerProva = null; }
      }, { threshold: .25 }).observe(secProva);
    }
    window.addEventListener('resize', posicao);
  }

  /* ════════ PAUSA — botão pequeno e discreto (WCAG 2.2.2). Para as animações CSS (html.pausado), o carrossel
     (window.__pausado, lido no andarProva) e todo vídeo que toca sozinho; avisa os módulos por lp:pausar/lp:retomar. ════════ */
  (function () {
    var b = d.getElementById('pausa'), raiz = d.documentElement, CHAVE = 'lp-pausa', parados = [];
    d.addEventListener('lp:retomar', function () {   // o vídeo da capa que nunca começou (pausa guardada) começa agora
      var v = d.getElementById('capa-video');
      if (v && v.paused && !reduzido && capa && capa.getBoundingClientRect().bottom > 0) { var r = v.play(); if (r && r.catch) r.catch(function () {}); }
    });
    if (!b) return;
    function aplica(p, medindo) {
      raiz.classList.toggle('pausado', p);
      window.__pausado = p;
      b.setAttribute('aria-pressed', p ? 'true' : 'false');
      b.setAttribute('aria-label', (p ? 'Retomar' : 'Pausar') + ' animações da página');
      b.title = (p ? 'Retomar' : 'Pausar') + ' animações';
      if (p) {
        parados = [].filter.call(d.querySelectorAll('video'), function (v) { return !v.paused; });
        parados.forEach(function (v) { v.pause(); });
      } else {
        parados.forEach(function (v) { var r = v.play(); if (r && r.catch) r.catch(function () {}); });
        parados = [];
      }
      try { d.dispatchEvent(new CustomEvent(p ? 'lp:pausar' : 'lp:retomar')); } catch (e) {}
      if (medindo) medir('pausa_animacoes', { estado: p ? 'pausa' : 'toca' });
    }
    b.addEventListener('click', function () {
      var p = !raiz.classList.contains('pausado');
      try { localStorage.setItem(CHAVE, p ? '1' : '0'); } catch (e) {}
      aplica(p, true);
    });
    var ini = false;
    try { ini = localStorage.getItem(CHAVE) === '1'; } catch (e) {}
    if (ini) aplica(true, false);
  })();

  /* ════════ 8 · FAQ ════════ */
  [].forEach.call(d.querySelectorAll('.faq details'), function (dt) {
    dt.addEventListener('toggle', function () {
      if (dt.open) medir('faq_abre', { pergunta: (dt.querySelector('summary') || {}).textContent });
    });
  });

  /* ════════ 9 · MAPA — entra só quando a pessoa chega perto ════════
     ⚠️ insertBefore, NUNCA appendChild (erro 12): o mapa cairia abaixo do link "Traçar rota". */
  var vao = d.getElementById('mapa');
  var montado = false;
  function montarMapa() {
    if (montado || !vao) return;
    montado = true;
    var url = vao.getAttribute('data-mapa');
    if (!url) return;
    var f = d.createElement('iframe');
    f.src = url;
    f.loading = 'lazy';
    f.title = 'Mapa com a localização da clínica';
    f.referrerPolicy = 'no-referrer-when-downgrade';
    f.setAttribute('allowfullscreen', '');
    f.addEventListener('load', function () {
      var v = d.getElementById('mapa-vazio');
      if (v) v.style.display = 'none';
    });
    vao.insertBefore(f, vao.firstChild);
  }
  quandoPerto(vao, 900, montarMapa);
})();
