\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{poster}[2012/05/04, Daniel Page <Daniel.Page@bristol.ac.uk>]

% =============================================================================

% parse class options

\RequirePackage{pgfkeys}
\RequirePackage{pgfopts}

\pgfkeys{/poster/.cd,
%     author = string
      author/.store in = \poster@author,
      author           = {},
% supervisor = string
  supervisor/.store in = \poster@supervisor,
  supervisor           = {},
%     degree = [BSc|MEng|MSci|MSc|PhD]
      degree/.store in = \poster@degree,
      degree           = {MEng},
%      title = string
       title/.store in = \poster@title@major,
       title           = {},
%   subtitle = string
    subtitle/.store in = \poster@title@minor,
    subtitle           = {},
%       type = string
        type/.store in = \poster@type,
        type           = {},
%       type = string
        year/.store in = \poster@year,
        year           = {\the\year}
}

\ProcessPgfOptions{/poster}

% load base class, then general-purpose packages

\LoadClass[final]{beamer}

% http://www.ctan.org/tex-archive/macros/latex/required/amslatex/
\RequirePackage{amsmath}
\RequirePackage{amssymb}
% http://tug.ctan.org/tex-archive/macros/latex/contrib/beamerposter/
\RequirePackage[orientation=portrait,size=a1,scale=1.5]{beamerposter}
% http://www.ctan.org/tex-archive/macros/latex/contrib/url
\RequirePackage{url}
% http://www.ctan.org/tex-archive/macros/latex/contrib/hyperref
\RequirePackage{hyperref}

% =============================================================================

\makeatletter

% -----------------------------------------------------------------------------

% configure hyperref

\hypersetup{colorlinks=true,bookmarks=false,urlcolor=red}

% -----------------------------------------------------------------------------

% define the official UoB red color as an RGB triple

\definecolor{uobred}{RGB}{191,47,56}

% configure the beamer package in a way that beamerposter can cope with

\usetheme[footheight=0.7cm]{boxes}
\usecolortheme{rose}

% configure the poster header

\setbeamertemplate{headline}{
  \leavevmode
  \begin{beamercolorbox}[wd=\paperwidth]{headline}
  \begin{columns}[c]
    \begin{column}{.50\linewidth}
      \begin{center}
        \vspace{4ex}
        \raggedright
        {\huge  {\poster@title@major}}                                                                     \\ [4ex]
        {\large {\textit\poster@title@minor}, Algorithm type: {\poster@type}} \\ [4ex]
        {\large {\poster@author}} \\ [4ex]
        {\large University of Bristol, Department of Computer Science}
        {{\poster@year}}
        \vspace{4ex}
      \end{center}
    \end{column}
    \begin{column}{.40\linewidth}
    \hfill
      \includegraphics[scale=0.48]{logo/5889.png}
    \end{column}
  \end{columns}
  \end{beamercolorbox}
}

% configure the poster footer

\setbeamertemplate{footline}{
  \leavevmode
  \begin{beamercolorbox}[wd=\paperwidth]{footline}
  \begin{columns}[c]
  \begin{column}{.45\paperwidth}
  \begin{center}
  \includegraphics[scale=0.8]{logo/logo_uob_color}
  \end{center}
  \end{column}
  \begin{column}{.45\paperwidth}
  \begin{center}
  \includegraphics[scale=0.6,trim=3.0cm 8.0cm 3.0cm 8.0cm,clip=true]{logo/logo_cs_qr}
  \end{center}
  \end{column}
  \end{columns}
  \end{beamercolorbox}
}

% configure beamer to match requirements of a poster rather than slides
\setbeamercolor{headline}{bg=uobred,fg=white}
\setbeamercolor{footline}{bg=white,fg=black}

\setbeamersize{text margin left=0.0cm}
\setbeamersize{text margin right=0.0cm}
\setbeamersize{sidebar width left=0cm}
\setbeamersize{sidebar width right=0cm}

\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{bibliography item}[text]

% -----------------------------------------------------------------------------

\makeatother

% =============================================================================
