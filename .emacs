
; https://melpa.org/#/getting-started
(require 'package)
(add-to-list 'package-archives
	     '("melpa" . "https://melpa.org/packages/") t)
(package-initialize)

; Source - https://stackoverflow.com/a/744681
; Posted by Bastien Léonard, modified by community. See post 'Timeline' for change history
; Retrieved 2026-02-04, License - CC BY-SA 3.0
; (setq inhibit-startup-screen t)

(column-number-mode)

(display-line-numbers-mode 1)

; https://emacs.stackexchange.com/questions/278/how-do-i-display-line-numbers-in-emacs-not-in-the-mode-line
; (add-hook 'prog-mode-hook 'display-line-numbers-mode)

;(tool-bar-mode 0)
; Source - https://stackoverflow.com/q/10152287
; Posted by Peter, modified by community. See post 'Timeline' for change history
; Retrieved 2026-02-09, License - CC BY-SA 3.0
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(calendar-date-style 'european)
 '(calendar-week-start-day 1)
 '(display-line-numbers 'relative)
 '(global-display-line-numbers-mode t)
 '(inhibit-startup-screen t)
 '(package-selected-packages '(gptel magit plantuml-mode fold-this))
 '(tool-bar-mode nil))

; https://www.perplexity.ai/search/mac-os-keyboard-insert-bracket-Czg2z_aSQ_uXztTOkzjbVQ
; make [] and {} under MacOS 
(setq mac-option-modifier nil
      mac-command-modifier 'meta)

; https://www.gnu.org/software/emacs/manual/html_mono/ido.html
(require 'ido)
(ido-mode t)

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

; mit M-x package-install-selected-packages werden die in der Config
; ausgewählen Pakete (unter package-selected-packages) installiert.
(package-install-selected-packages)

; GPTel
; https://gptel.org/manual.html
(gptel-make-ollama
   "Ollama"
   :host "localhost:11434"
   :models '(ministralstral:latest)
   :stream t)

; Github Copilot
;(gptel-make-gh-copilot "Copilot")

; MistralLeChat
;(gptel-make-openai "MistralLeChat"  ;Any name you want
;  :host "api.mistral.ai"
;  :endpoint "/v1/chat/completions"
;  :protocol "https"
;  :stream t
;  :models '("mistral-small"))

(gptel-make-openai "LMStudio"
  :host "localhost:1234"
  :endpoint "/v1/chat/completions"
  :protocol "http"
  :stream t
  :models
  '(llama-3.2-3b-instruct
    mistralai/ministral-3-3b
    google/gemma-3-4b
    deepseek/deepseek-r1-0528-qwen3-8b
    starcoder2-7b))

; configure default model and backend
(setq
 gptel-model 'MistralLeChat
 gptel-backend (gptel-make-openai "MistralLeChat"
		 :host "api.mistral.ai"
		 :endpoint "/v1/chat/completions"
		 :protocol "https"
		 :stream t
		 :models '("mistral-small" "mistral-medium" "mistral-large")))

