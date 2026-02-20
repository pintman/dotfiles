
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

; change default settings (font, size) on Mac
(if (eq system-type 'darwin)
    (setq default-frame-alist
	  '((font . "Menlo-14") (width . 150))))
; https://www.perplexity.ai/search/mac-os-keyboard-insert-bracket-Czg2z_aSQ_uXztTOkzjbVQ
; make [] and {} under MacOS 
(setq mac-option-modifier nil
      mac-command-modifier 'meta)

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
 '(ido-enable-flex-matching t)
 '(inhibit-startup-screen t)
 '(package-selected-packages '(gptel magit plantuml-mode fold-this))
 '(tool-bar-mode nil))

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

; Ollama
(gptel-make-ollama
   "Ollama"
   :host "localhost:11434"
   :models '(ministralstral:latest)
   :stream t)

; LMStudio
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
    starcoder2-7b
    openai/gpt-oss-20b))

; MistralLeChat
(gptel-make-openai "MistralLeChat"
  :host "api.mistral.ai"
  :endpoint "/v1/chat/completions"
  :key #'gptel-api-key-from-auth-source
  :protocol "https"
  :stream t
  :models '("mistral-small" "mistral-medium" "mistral-large"))

; OpenRouter
; https://gptel.org/manual.html#orgf4cd09b
;; OpenRouter offers an OpenAI compatible API
(gptel-make-openai "OpenRouter"
  :host "openrouter.ai"
  :endpoint "/api/v1/chat/completions"
  :key #'gptel-api-key-from-auth-source
  :stream t
  :models '(openai/gpt-3.5-turbo
            mistralai/mixtral-8x7b-instruct
            meta-llama/codellama-34b-instruct
            codellama/codellama-70b-instruct
            google/gemini-pro
	    deepseek/deepseek-r1-0528:free
	    deepseek/deepseek-chat-v3.1
	    google/gemini-2.5-flash-lite))

; configure default model and backend
(setq
 gptel-model 'claude-sonnet-4.5
 gptel-backend ; Github Copilot
 (gptel-make-gh-copilot "Copilot"))

