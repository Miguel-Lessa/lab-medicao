"""Estilo padrao para graficos Plotly — legendas e rotulos legiveis."""

from __future__ import annotations

import plotly.graph_objects as go

FONT_FAMILY = "Arial, Helvetica, sans-serif"
TITLE_SIZE = 22
AXIS_TITLE_SIZE = 17
TICK_SIZE = 15
LEGEND_SIZE = 16
COLORBAR_TITLE_SIZE = 16
COLORBAR_TICK_SIZE = 14
PIE_TEXT_SIZE = 15


def _base_axis_style() -> dict:
    return dict(
        title_font=dict(size=AXIS_TITLE_SIZE, family=FONT_FAMILY),
        tickfont=dict(size=TICK_SIZE, family=FONT_FAMILY),
    )


def style_figure(
    fig: go.Figure,
    *,
    legend_below: bool = False,
    legend_right: bool = False,
    wide_y_labels: bool = False,
    bottom_margin: int | None = None,
    left_margin: int | None = None,
    right_margin: int | None = None,
    top_margin: int | None = None,
) -> go.Figure:
    """Aplica fontes maiores em titulo, eixos, legenda e margens."""
    margin = dict(
        l=left_margin or (220 if wide_y_labels else 90),
        r=right_margin or (240 if legend_right else 40),
        t=top_margin or 90,
        b=bottom_margin or (160 if legend_below else 80),
    )

    legend = dict(
        font=dict(size=LEGEND_SIZE, family=FONT_FAMILY),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#cccccc",
        borderwidth=1,
        tracegroupgap=8,
        itemsizing="constant",
    )
    if legend_below:
        legend.update(orientation="h", yanchor="top", y=-0.28, x=0.5, xanchor="center")
    elif legend_right:
        legend.update(orientation="v", yanchor="middle", y=0.5, x=1.02, xanchor="left")
    else:
        legend.update(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center")

    title_text = ""
    if fig.layout.title and fig.layout.title.text:
        title_text = fig.layout.title.text

    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=TICK_SIZE),
        title=dict(text=title_text, font=dict(size=TITLE_SIZE, family=FONT_FAMILY)),
        legend=legend,
        margin=margin,
        xaxis=_base_axis_style(),
        yaxis=_base_axis_style(),
    )

    # Eixos extras (Pareto, subplots)
    fig.update_xaxes(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=TICK_SIZE))
    fig.update_yaxes(title_font=dict(size=AXIS_TITLE_SIZE), tickfont=dict(size=TICK_SIZE))

    if hasattr(fig.layout, "coloraxis") and fig.layout.coloraxis:
        fig.update_layout(
            coloraxis_colorbar=dict(
                title_font=dict(size=COLORBAR_TITLE_SIZE),
                tickfont=dict(size=COLORBAR_TICK_SIZE),
                len=0.75,
                thickness=22,
            )
        )

    return fig


def style_bar_horizontal(fig: go.Figure) -> go.Figure:
    return style_figure(fig, wide_y_labels=True, left_margin=260)


def style_line_multi(fig: go.Figure, n_series: int = 5) -> go.Figure:
    bottom = 200 if n_series > 4 else 160
    fig.update_traces(line=dict(width=2.8), marker=dict(size=9))
    return style_figure(fig, legend_below=True, bottom_margin=bottom)


def style_pie(fig: go.Figure) -> go.Figure:
    fig.update_traces(
        textfont=dict(size=PIE_TEXT_SIZE, family=FONT_FAMILY),
        textposition="inside",
        insidetextorientation="radial",
    )
    return style_figure(fig, legend_right=True, right_margin=320, left_margin=40)


def style_pareto(fig: go.Figure) -> go.Figure:
    fig.update_layout(xaxis_tickangle=-40)
    fig.update_traces(marker=dict(size=10), selector=dict(type="scatter"))
    return style_figure(fig, legend_below=True, bottom_margin=220, top_margin=100)


def style_box(fig: go.Figure) -> go.Figure:
    fig.update_xaxes(tickangle=-35)
    return style_figure(fig, legend_below=False, bottom_margin=140, left_margin=90)


def style_heatmap(fig: go.Figure) -> go.Figure:
    fig.update_xaxes(tickangle=-35)
    return style_figure(fig, wide_y_labels=True, left_margin=100, bottom_margin=180, right_margin=120)


def style_simple(fig: go.Figure) -> go.Figure:
    return style_figure(fig)
