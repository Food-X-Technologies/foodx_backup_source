
.PHONY: install-pre-commit-hooks
install-pre-commit-hooks:
	pre-commit \
	  install \
	    --install-hooks
