; Source - https://stackoverflow.com/a/744681
; Posted by Bastien Léonard, modified by community. See post 'Timeline' for change history
; Retrieved 2026-02-04, License - CC BY-SA 3.0
(setq inhibit-startup-screen t)

(column-number-mode)

; https://emacs.stackexchange.com/questions/278/how-do-i-display-line-numbers-in-emacs-not-in-the-mode-line
(add-hook 'prog-mode-hook 'display-line-numbers-mode)

;(tool-bar-mode 0)
; Source - https://stackoverflow.com/q/10152287
; Posted by Peter, modified by community. See post 'Timeline' for change history
; Retrieved 2026-02-09, License - CC BY-SA 3.0
(custom-set-variables
  '(tool-bar-mode nil)
)



