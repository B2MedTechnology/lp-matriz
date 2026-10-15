-- ═══════════════════════════════════════════════════════════════════════════════════════════
-- 0001 — Fábrica de landing pages: a fila de pedidos e a configuração da Diretoria (Postgres/Supabase)
-- Pré-requisito: 0000_pre_requisitos.sql (a tabela `clientes`, se o banco ainda não tiver um cadastro).
--
-- POR QUE ASSIM: o painel mostra custo e tempo ESTIMADOS antes do "Gerar" (validado contra páginas aprovadas: US$ 0,45–0,57 e
-- 5–8 min por página) e o preço do cliente NUNCA vai na página (sempre "informado pelo WhatsApp").
--
-- O QUE MUDA:
--   1. `lp_config` (uma linha): modelo da IA, custo e tempo estimados por página (o que o dash mostra antes do "Gerar"), teto de
--      gasto no mês, cotação para mostrar em reais, ligada/desligada. Sem segredo nenhum aqui (chaves ficam no cofre de segredos / ambiente da fábrica).
--   2. `lp_pedidos`: cada "Gerar" do assessor vira uma linha; a fábrica (o contêiner da fábrica na VPS) pega da fila, anda pelas etapas
--      (etapa + progresso + previsão de fim), grava custo real, link da prévia e a lista "falta decidir" (pendências).
--   3. Leituras do painel (chave anon, sem o texto do briefing): `lp_config_ver()`, `lp_pedidos_list(p_assessor)`.
--   4. Escritas só service_role: `lp_pedido_acao` (dash `api/lp-pedido`, que prova quem pede), `lp_config_salvar` (idem, só
--      Diretoria) e `lp_pedido_pegar` (a fábrica pega o próximo da fila sem disputar: `for update skip locked`).
-- Voltar: _ROLLBACK (drop das funções e das tabelas — as prévias já publicadas na Vercel continuam lá).
-- ═══════════════════════════════════════════════════════════════════════════════════════════

begin;

do $$
begin
  if to_regclass('public.lp_pedidos') is not null or to_regclass('public.lp_config') is not null then
    raise exception 'ABORTA 0001: lp_pedidos/lp_config já existem';
  end if;
end $$;

create table public.lp_config (
  id                   smallint primary key default 1 check (id = 1),
  ligada               boolean not null default true,
  modelo               text not null default 'google/gemini-2.5-pro',
  custo_estimado_usd   numeric(8,2) not null default 0.55 check (custo_estimado_usd >= 0),
  tempo_estimado_seg   integer not null default 480 check (tempo_estimado_seg > 0),
  teto_mes_usd         numeric(8,2) not null default 30 check (teto_mes_usd >= 0),
  cotacao_brl          numeric(6,2) not null default 5.50 check (cotacao_brl > 0),
  atualizado_por       text,
  atualizado_em        timestamptz not null default now()
);
insert into public.lp_config (id) values (1);
alter table public.lp_config enable row level security;
comment on table public.lp_config is
  'Configuração da fábrica de landing pages (uma linha). Escrita: lp_config_salvar (dash api/lp-pedido, só Diretoria) · Leitura: lp_config_ver (painel). Sem segredo. [0001, 28-09]';

create table public.lp_pedidos (
  id                 bigserial primary key,
  cliente_id         uuid references public.clientes(id) on delete set null,
  cliente_nome       text not null,
  assessor           text,
  pedido_por         text not null,
  area               text not null default 'medico' check (area in ('medico', 'dentista', 'advogado', 'fisioterapeuta')),
  termo              text not null,
  instagram          text,
  perfil_google      text,
  drive_url          text,
  conselho_registro  text,
  briefing           text,
  observacoes        text,
  status             text not null default 'na_fila' check (status in ('na_fila', 'gerando', 'pronta', 'erro', 'cancelada')),
  etapa              text,
  progresso          smallint not null default 0 check (progresso between 0 and 100),
  previsao_fim       timestamptz,
  iniciado_em        timestamptz,
  concluido_em       timestamptz,
  custo_usd          numeric(8,4),
  previa_url         text,
  pendencias         jsonb not null default '[]'::jsonb,
  erro               text,
  criado_em          timestamptz not null default now(),
  atualizado_em      timestamptz not null default now()
);
create index lp_pedidos_fila on public.lp_pedidos (criado_em) where status = 'na_fila';
create index lp_pedidos_assessor on public.lp_pedidos (assessor, criado_em desc);
alter table public.lp_pedidos enable row level security;
comment on table public.lp_pedidos is
  'Pedidos de landing page (um por "Gerar"). Escrita: lp_pedido_acao (dash api/lp-pedido) e a fábrica na VPS (service_role) · Leitura: lp_pedidos_list (painel, sem o briefing). [0001, 28-09]';

-- ── leituras do painel ─────────────────────────────────────────────────────────────────────

create function public.lp_config_ver()
returns jsonb
language sql
stable
security definer
set search_path = public
as $fn$
  select jsonb_build_object(
           'ligada', c.ligada, 'modelo', c.modelo, 'custo_estimado_usd', c.custo_estimado_usd,
           'tempo_estimado_seg', c.tempo_estimado_seg, 'teto_mes_usd', c.teto_mes_usd, 'cotacao_brl', c.cotacao_brl,
           'atualizado_por', c.atualizado_por, 'atualizado_em', c.atualizado_em,
           'gasto_mes_usd', (select coalesce(sum(p.custo_usd), 0) from public.lp_pedidos p
                              where p.criado_em >= date_trunc('month', now() at time zone 'America/Manaus') at time zone 'America/Manaus'),
           'paginas_mes', (select count(*) from public.lp_pedidos p
                            where p.status = 'pronta'
                              and p.criado_em >= date_trunc('month', now() at time zone 'America/Manaus') at time zone 'America/Manaus'),
           'custo_medio_real_usd', (select round(avg(p.custo_usd), 2) from (select custo_usd from public.lp_pedidos
                                     where status = 'pronta' and custo_usd is not null order by concluido_em desc limit 20) p),
           'tempo_medio_real_seg', (select round(avg(extract(epoch from (concluido_em - iniciado_em))))::int from (select concluido_em, iniciado_em from public.lp_pedidos
                                     where status = 'pronta' and iniciado_em is not null order by concluido_em desc limit 20) t),
           'na_fila', (select count(*) from public.lp_pedidos where status in ('na_fila', 'gerando')))
    from public.lp_config c where c.id = 1;
$fn$;
revoke all on function public.lp_config_ver() from public, anon, authenticated;
grant execute on function public.lp_config_ver() to anon, authenticated, service_role -- exposto-porque: o formulário do assessor mostra o custo e o tempo estimados antes do "Gerar"; só números de operação, sem segredo nem dado de cliente
;
comment on function public.lp_config_ver() is
  'Configuração da fábrica + gasto do mês e médias reais (custo/tempo das últimas 20 páginas prontas). [0001]';

create function public.lp_pedidos_list(p_assessor text default null)
returns jsonb
language sql
stable
security definer
set search_path = public
as $fn$
  select coalesce(jsonb_agg(to_jsonb(t) order by t.criado_em desc), '[]'::jsonb)
  from (
    select p.id, p.cliente_id, p.cliente_nome, p.assessor, p.pedido_por, p.area, p.termo, p.instagram, p.perfil_google,
           p.drive_url, p.status, p.etapa, p.progresso, p.previsao_fim, p.iniciado_em, p.concluido_em, p.custo_usd,
           p.previa_url, p.pendencias, p.erro, p.criado_em
      from public.lp_pedidos p
     where (p_assessor is null or p.assessor = p_assessor or p.pedido_por = p_assessor)
       and p.criado_em > now() - interval '90 days'
     order by p.criado_em desc
     limit 200
  ) t;
$fn$;
revoke all on function public.lp_pedidos_list(text) from public, anon, authenticated;
grant execute on function public.lp_pedidos_list(text) to anon, authenticated, service_role -- exposto-porque: o painel do assessor acompanha os pedidos dele com a chave anon, como as outras listas; o texto do briefing NÃO sai daqui
;
comment on function public.lp_pedidos_list(text) is
  'Pedidos de landing page dos últimos 90 dias (do assessor, ou todos com null), sem o briefing. [0001]';

-- ── escritas (só service_role) ─────────────────────────────────────────────────────────────

create function public.lp_pedido_acao(
  p_acao text, p_quem text, p_diretoria boolean default false, p_id bigint default null, p_dados jsonb default '{}'::jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $fn$
declare
  v_cfg public.lp_config;
  v_ped public.lp_pedidos;
  v_cli public.clientes;
  v_gasto numeric;
  v_novo bigint;
begin
  select * into v_cfg from public.lp_config where id = 1;
  if p_acao = 'criar' then
    if not v_cfg.ligada then return jsonb_build_object('ok', false, 'codigo', 'fabrica_desligada'); end if;
    select coalesce(sum(custo_usd), 0) into v_gasto from public.lp_pedidos
     where criado_em >= date_trunc('month', now() at time zone 'America/Manaus') at time zone 'America/Manaus';
    if v_gasto + v_cfg.custo_estimado_usd > v_cfg.teto_mes_usd then
      return jsonb_build_object('ok', false, 'codigo', 'teto_do_mes', 'gasto_mes_usd', v_gasto, 'teto_mes_usd', v_cfg.teto_mes_usd);
    end if;
    if nullif(trim(p_dados->>'cliente_id'), '') is not null then
      select * into v_cli from public.clientes where id = (p_dados->>'cliente_id')::uuid;
      if not found then return jsonb_build_object('ok', false, 'codigo', 'cliente_inexistente'); end if;
      if not p_diretoria and v_cli.assessor is distinct from p_quem then
        return jsonb_build_object('ok', false, 'codigo', 'fora_da_carteira');
      end if;
    end if;
    if length(coalesce(trim(p_dados->>'termo'), '')) < 3 then return jsonb_build_object('ok', false, 'codigo', 'falta_termo'); end if;
    if length(coalesce(trim(p_dados->>'briefing'), '')) < 200 and length(coalesce(trim(v_cli.briefing), '')) < 200 then
      return jsonb_build_object('ok', false, 'codigo', 'falta_briefing');
    end if;
    insert into public.lp_pedidos (cliente_id, cliente_nome, assessor, pedido_por, area, termo, instagram, perfil_google, drive_url,
                                   conselho_registro, briefing, observacoes, previsao_fim)
    values (v_cli.id, coalesce(v_cli.nome, nullif(trim(p_dados->>'cliente_nome'), ''), 'sem nome'),
            coalesce(v_cli.assessor, case when p_diretoria then null else p_quem end), p_quem,
            coalesce(nullif(p_dados->>'area', ''), 'medico'), trim(p_dados->>'termo'),
            nullif(trim(p_dados->>'instagram'), ''), nullif(trim(p_dados->>'perfil_google'), ''),
            nullif(trim(p_dados->>'drive_url'), ''), nullif(trim(p_dados->>'conselho_registro'), ''),
            coalesce(nullif(trim(p_dados->>'briefing'), ''), v_cli.briefing), nullif(trim(p_dados->>'observacoes'), ''),
            now() + make_interval(secs => v_cfg.tempo_estimado_seg))
    returning id into v_novo;
    return jsonb_build_object('ok', true, 'id', v_novo);
  end if;

  select * into v_ped from public.lp_pedidos where id = p_id for update;
  if not found then return jsonb_build_object('ok', false, 'codigo', 'pedido_inexistente'); end if;
  if not p_diretoria and v_ped.pedido_por is distinct from p_quem and v_ped.assessor is distinct from p_quem then
    return jsonb_build_object('ok', false, 'codigo', 'fora_da_carteira');
  end if;
  if p_acao = 'cancelar' then
    if v_ped.status <> 'na_fila' then return jsonb_build_object('ok', false, 'codigo', 'ja_comecou'); end if;
    update public.lp_pedidos set status = 'cancelada', atualizado_em = now() where id = p_id;
    return jsonb_build_object('ok', true);
  elsif p_acao = 'refazer' then
    if v_ped.status not in ('erro', 'pronta', 'cancelada') then return jsonb_build_object('ok', false, 'codigo', 'ainda_rodando'); end if;
    update public.lp_pedidos
       set status = 'na_fila', etapa = null, progresso = 0, erro = null, iniciado_em = null, concluido_em = null,
           observacoes = coalesce(nullif(trim(p_dados->>'observacoes'), ''), observacoes),
           previsao_fim = now() + make_interval(secs => v_cfg.tempo_estimado_seg), atualizado_em = now()
     where id = p_id;
    return jsonb_build_object('ok', true);
  end if;
  return jsonb_build_object('ok', false, 'codigo', 'acao_invalida');
end;
$fn$;
revoke all on function public.lp_pedido_acao(text, text, boolean, bigint, jsonb) from public, anon, authenticated;
grant execute on function public.lp_pedido_acao(text, text, boolean, bigint, jsonb) to service_role;
comment on function public.lp_pedido_acao(text, text, boolean, bigint, jsonb) is
  'criar / cancelar / refazer um pedido de landing page. Quem pede é provado pela rota do dash (api/lp-pedido); o assessor só pede para cliente dele. Respeita ligada e o teto do mês. [0001]';

create function public.lp_config_salvar(p_quem text, p_dados jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $fn$
begin
  update public.lp_config
     set ligada             = coalesce((p_dados->>'ligada')::boolean, ligada),
         modelo             = coalesce(nullif(trim(p_dados->>'modelo'), ''), modelo),
         custo_estimado_usd = coalesce((p_dados->>'custo_estimado_usd')::numeric, custo_estimado_usd),
         tempo_estimado_seg = coalesce((p_dados->>'tempo_estimado_seg')::integer, tempo_estimado_seg),
         teto_mes_usd       = coalesce((p_dados->>'teto_mes_usd')::numeric, teto_mes_usd),
         cotacao_brl        = coalesce((p_dados->>'cotacao_brl')::numeric, cotacao_brl),
         atualizado_por     = p_quem,
         atualizado_em      = now()
   where id = 1;
  return public.lp_config_ver();
end;
$fn$;
revoke all on function public.lp_config_salvar(text, jsonb) from public, anon, authenticated;
grant execute on function public.lp_config_salvar(text, jsonb) to service_role;
comment on function public.lp_config_salvar(text, jsonb) is
  'Diretoria salva a configuração da fábrica (dash api/lp-pedido, acao=config). [0001]';

create function public.lp_pedido_pegar()
returns setof public.lp_pedidos
language sql
security definer
set search_path = public
as $fn$
  update public.lp_pedidos p
     set status = 'gerando', etapa = 'começando', progresso = 2, iniciado_em = now(), atualizado_em = now(),
         previsao_fim = now() + make_interval(secs => (select tempo_estimado_seg from public.lp_config where id = 1))
   where p.id = (select id from public.lp_pedidos where status = 'na_fila' order by criado_em limit 1 for update skip locked)
  returning p.*;
$fn$;
revoke all on function public.lp_pedido_pegar() from public, anon, authenticated;
grant execute on function public.lp_pedido_pegar() to service_role;
comment on function public.lp_pedido_pegar() is
  'A fábrica (VPS) pega o próximo pedido da fila e o marca como gerando. [0001]';

commit;
