# -*- coding: utf-8 -*-
import json
from math import sqrt
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
IN = BASE / "inputs"
OUT = BASE / "outputs"

def load_config():
    cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
    cfg["start_date"] = pd.to_datetime(cfg["start_date"]).date()
    return cfg

def read_nav():
    df = pd.read_csv(IN / "nav_diario.csv", parse_dates=["date"])
    df = df.sort_values("date").dropna()
    if "nav_fundo" not in df or "cdi_diario" not in df:
        raise ValueError("nav_diario.csv precisa conter colunas: date, nav_fundo, cdi_diario")
    return df

def period_return_from_nav(df, start, end):
    """Geometric return from daily NAV between inclusive dates [start, end]."""
    d = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))].copy()
    if d.shape[0] < 2:
        return np.nan
    nav0, nav1 = d["nav_fundo"].iloc[0], d["nav_fundo"].iloc[-1]
    return float(nav1 / nav0 - 1.0)

def period_return_from_cdi(df, start, end):
    d = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))].copy()
    if d.empty:
        return np.nan
    acc = (1.0 + d["cdi_diario"]).prod() - 1.0
    return float(acc)

def annualized_vol_from_daily(df, window_days=252):
    """Annualized vol from last `window_days` daily returns (log or simple)."""
    d = df.tail(window_days).copy()
    d["ret"] = d["nav_fundo"].pct_change()
    vol = float(d["ret"].std(ddof=1) * sqrt(252)) if d["ret"].notna().sum() > 2 else np.nan
    return vol

def month_bounds(last_date):
    first = pd.to_datetime(last_date).replace(day=1)
    last = (first + pd.offsets.MonthEnd(0))
    return first.date(), last.date()

def year_bounds(last_date):
    first = pd.to_datetime(last_date).replace(month=1, day=1)
    last = last_date
    return first.date(), last.date()

def make_performance_table(cfg, nav):
    last_date = nav["date"].max().date()
    month_start, month_end = month_bounds(last_date)
    ytd_start, ytd_end = year_bounds(last_date)

    def period(years):
        start = last_date.replace(year=last_date.year - years)
        # If start < first available date, clamp
        start = max(start, nav["date"].min().date())
        return start, last_date

    periods = [
        ("Mês", month_start, month_end),
        ("Ano", ytd_start, ytd_end),
        ("12 meses", *period(1)),
        ("24 meses", *period(2)),
        ("36 meses", *period(3)),
        ("Início", cfg["start_date"], last_date),
    ]

    rows = []
    for label, start, end in periods:
        rf = period_return_from_nav(nav, start, end)
        rc = period_return_from_cdi(nav, start, end)
        pct_cdi = (rf / rc * 100.0) if pd.notna(rf) and pd.notna(rc) and rc != 0 else np.nan
        rows.append([label, rf, rc, pct_cdi])

    df = pd.DataFrame(rows, columns=["Período", "Fundo", "CDI", "% CDI"])
    df["Vol*"] = annualized_vol_from_daily(nav, 252)
    df["PL Médio"] = cfg.get("pl_medio", np.nan)
    # Format friendly copy to Excel
    df_x = df.copy()
    with pd.ExcelWriter(OUT / "tabela_performance.xlsx", engine="xlsxwriter") as xw:
        df_x.to_excel(xw, sheet_name="Performance", index=False)
        ws = xw.sheets["Performance"]
        # Formats
        workbook = xw.book
        pct = workbook.add_format({"num_format": "0.00%"})
        pct_no_sign = workbook.add_format({"num_format": "0.00"})
        money = workbook.add_format({"num_format": "R$ #,##0"})
        # Apply formats
        ws.set_column("A:A", 16)
        ws.set_column("B:C", 12, pct)
        ws.set_column("D:D", 10, pct_no_sign)  # %CDI em pontos percentuais do CDI
        ws.set_column("E:E", 10, pct)          # Vol*
        ws.set_column("F:F", 16, money)

    return df

def read_attribution():
    p = IN / "pnl_atribuicao_diario.csv"
    if not p.exists(): 
        return None
    df = pd.read_csv(p, parse_dates=["date"]).sort_values("date")
    return df

def plot_attribution_month(df, last_date):
    # sum per bucket for the last month
    first, last = month_bounds(last_date)
    d = df[(df["date"] >= pd.to_datetime(first)) & (df["date"] <= pd.to_datetime(last))].copy()
    if d.empty:
        return
    buckets = [c for c in d.columns if c != "date"]
    contrib = d[buckets].sum()
    # Plot
    plt.figure()
    contrib.plot(kind="bar")
    plt.title("Atribuição de Performance – Mês")
    plt.ylabel("% do PL (ou bps/10000)")
    plt.xlabel("Buckets")
    plt.tight_layout()
    plt.savefig(OUT / "atribuicao_mes.png", dpi=160)
    plt.close()

def plot_lines(csv_name, title, outfile, ylabel="%"):
    p = IN / csv_name
    if not p.exists(): 
        return
    df = pd.read_csv(p)
    if "data" not in df.columns:
        return
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m")
    df = df.sort_values("data")
    x = df["data"]
    plt.figure()
    for col in df.columns:
        if col == "data": 
            continue
        plt.plot(x, df[col], label=col)
    plt.title(title)
    plt.xlabel("Período")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / outfile, dpi=160)
    plt.close()

def main():
    cfg = load_config()
    nav = read_nav()
    perf = make_performance_table(cfg, nav)
    last_date = nav["date"].max()

    # Attribution (optional)
    attr = read_attribution()
    if attr is not None:
        plot_attribution_month(attr, last_date)

    # Lines
    plot_lines("acoes_rentab_mensal.csv", "Fundos de ações ativos – Evolução da Rentabilidade (%)", "evolucao_acoes_ativos.png", "%")
    plot_lines("setoriais_rentab_mensal.csv", "Fundos de ações setoriais – Evolução da Rentabilidade (%)", "evolucao_acoes_setoriais.png", "%")
    plot_lines("indices_rentab_mensal.csv", "Índices – Evolução (%)", "indices_evolucao.png", "%")

    print("Arquivos gerados em:", OUT)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True, parents=True)
    main()
