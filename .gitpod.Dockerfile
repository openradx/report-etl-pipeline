FROM gitpod/workspace-python-3.12

USER gitpod

RUN python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    python3 -m pipx install invoke && \
    invoke --print-completion-script=bash >> $HOME/.bash_completion

RUN python3 -m pipx install uv && \
    uv generate-shell-completion bash >> $HOME/.bash_completion
