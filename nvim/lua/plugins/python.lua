return {
  -- Pyright LSP (strict type checking)
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        pyright = {
          settings = {
            python = {
              analysis = {
                typeCheckingMode = "strict",
              },
            },
          },
        },
      },
    },
  },

  -- Format on save with Black
  {
    "stevearc/conform.nvim",
    opts = function(_, opts)
      opts.formatters_by_ft = opts.formatters_by_ft or {}
      opts.formatters_by_ft.python = { "black" }
      return opts
    end,
  },

  -- Lint with Flake8 and mypy
  {
    "mfussenegger/nvim-lint",
    opts = function(_, opts)
      opts.linters_by_ft = opts.linters_by_ft or {}
      opts.linters_by_ft.python = { "flake8", "mypy" }
      return opts
    end,
  },

  -- Mason: install Python tools
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        "black",
        "flake8",
        "mypy",
        "pyright",
      },
    },
  },
}
