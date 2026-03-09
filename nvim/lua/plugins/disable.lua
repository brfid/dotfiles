return {
  -- Security: sends buffer contents to external AI APIs
  { "yetone/avante.nvim", enabled = false },

  -- UI chrome: heavy replacement of native cmdline/messages/search
  { "folke/noice.nvim", enabled = false },
  { "MunifTanjim/nui.nvim", enabled = false },


  -- Redundant colorscheme (keeping tokyonight)
  { "catppuccin/nvim", enabled = false },

  -- Lua/Neovim plugin development only
  { "folke/lazydev.nvim", enabled = false },

  -- HTML/JSX auto-close tags
  { "windwp/nvim-ts-autotag", enabled = false },

  -- Premade snippet library
  { "rafamadriz/friendly-snippets", enabled = false },

  -- Session restore
  { "folke/persistence.nvim", enabled = false },

  -- Project-wide find/replace UI
  { "MagicDuck/grug-far.nvim", enabled = false },

  -- TODO/FIXME highlighting
  { "folke/todo-comments.nvim", enabled = false },
}
