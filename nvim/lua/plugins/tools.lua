return {
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        "json-lsp",
        "shellcheck",
        "shfmt",
        "stylua",
        "yaml-language-server",
      },
    },
  },
}
