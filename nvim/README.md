# nvim

Neovim should be generated as a local LazyVim-based config, not symlinked
back to this repo. This folder is a rebuild capsule: it describes the durable
editor preferences and the plugin shape an LLM should adapt into
`~/.config/nvim` for the current machine.

Live path:
- `~/.config/nvim/`

Do not symlink the live config to `~/src/dotfiles/nvim`. Copy or generate a
real local config directory instead. Runtime files such as `lazy-lock.json`,
`lazyvim.json`, plugin clones, Mason state, shada, swap, undo, caches, and logs
stay outside git.

## Base

Use LazyVim as the base distribution with local plugin specs under
`lua/plugins/` and local config under `lua/config/`.

Expected bootstrap shape:

```lua
require("config.lazy")
```

The Lazy setup should import LazyVim and local plugin specs:

```lua
require("lazy").setup({
  spec = {
    { "LazyVim/LazyVim", import = "lazyvim.plugins" },
    { import = "plugins" },
  },
  defaults = {
    lazy = false,
    version = false,
  },
  install = { colorscheme = { "tokyonight", "habamax" } },
  checker = {
    enabled = false,
    notify = false,
  },
})
```

## Terminal And Icons

Assume the terminal uses a Nerd Font-capable monospace. Do not add ASCII icon
fallback overrides for LazyVim, lualine, mini.icons, or dashboard unless the
target terminal lacks Nerd Font support.

Keep LazyVim's default lualine and Bufferline icon behavior.

## UI Plugins

Keep LazyVim Bufferline enabled for buffer tabs. Do not disable
`akinsho/bufferline.nvim`.

Do not add Dropbar by default. The outline is the preferred structure
navigation surface; Dropbar adds duplicate UI chrome for this setup. Include
it in the disabled plugins list in `disable.lua`.

Use Snacks Explorer as the file explorer. Keep the sidebar compact:

```lua
return {
  "folke/snacks.nvim",
  opts = {
    picker = {
      layouts = {
        sidebar = {
          layout = {
            width = 30,
            min_width = 30,
          },
        },
      },
    },
  },
}
```

Use `hedyhli/outline.nvim` as the symbol outline on `<leader>o`. It should open
without stealing focus and use a fixed width around 25 columns.

## Disabled Plugins

Disable plugins that add unwanted surface area or duplicate this setup:

- `yetone/avante.nvim` because it can send buffer contents to external AI APIs.
- `folke/noice.nvim` and `MunifTanjim/nui.nvim` because they heavily replace
  native command line, messages, and search UI.
- `catppuccin/nvim` when using Tokyo Night.
- `folke/lazydev.nvim` unless doing Lua/Neovim plugin development.
- `Bekaboo/dropbar.nvim`.
- `windwp/nvim-ts-autotag`.
- `rafamadriz/friendly-snippets`.
- `folke/persistence.nvim`.
- `MagicDuck/grug-far.nvim`.
- `folke/todo-comments.nvim`.

## Language Tooling

Configure `nvim-lspconfig` for:

- `jsonls`
- `yamlls`, with SchemaStore enabled
- `pyright`, with basic Python type checking

These LSP servers are auto-installed by mason-lspconfig; do not duplicate them
in Mason's `ensure_installed`.

Configure `mason.nvim` `ensure_installed` for non-LSP tools only:

- `shellcheck`
- `shfmt`
- `stylua`
- `black`
- `flake8`

Configure Python formatting and linting:

- `conform.nvim` uses `black` for Python.
- `nvim-lint` uses `flake8` for Python.

Do not run `mypy` globally by default. Add it only for projects that actually
use typed Python and benefit from project-specific type checking.

## Editing Behavior

Preserve these local editing preferences:

- `vim.opt.selection = "exclusive"`
- Fill characters:
  - `eob = " "`
  - `fold = " "`
  - `foldopen = "-"`
  - `foldclose = "+"`
  - `foldsep = " "`
  - `diff = "/"`

Keep insert-mode arrow behavior friendly to soft-wrapped text:

```lua
vim.keymap.set("i", "<Up>", "<C-o>gk", { noremap = true, silent = true })
vim.keymap.set("i", "<Down>", "<C-o>gj", { noremap = true, silent = true })
vim.keymap.set("i", "<Home>", "<C-o>g0", { noremap = true, silent = true })
vim.keymap.set("i", "<End>", "<C-o>g$", { noremap = true, silent = true })
```

Keep Shift-arrow selection in normal, visual, and insert modes. Keep familiar
editor shortcuts:

- `<C-a>` selects all.
- `<C-p>` opens the Snacks file picker.
- `<C-f>` opens Snacks project search.

`<C-s>` save is a LazyVim default; do not re-map it.

## Autocmds

Keep these local autocmd behaviors:

- Remove background highlighting from inline Markdown code whenever the color
  scheme changes, and once during startup.

`autoread` and `checktime` on focus are LazyVim defaults; do not duplicate them.

## Local Verification

After generating the live config, run a headless startup check:

```sh
nvim -i NONE --headless '+lua print("startup ok")' '+qa'
```

For this setup, a loaded UI should have Bufferline owning `tabline` and lualine
setting `laststatus=3`.
