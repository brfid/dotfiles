return {
  -- Use ASCII fallbacks so Terminal.app does not need a Nerd Font.
  {
    "nvim-mini/mini.icons",
    opts = {
      style = "ascii",
    },
  },

  -- LazyVim icon table used by statusline, diagnostics, git, completion, etc.
  {
    "LazyVim/LazyVim",
    opts = function(_, opts)
      opts.icons = opts.icons or {}
      local icons = opts.icons

      icons.misc = vim.tbl_extend("force", icons.misc or {}, {
        dots = "...",
      })

      icons.ft = {
        octo = "GH ",
        gh = "GH ",
        ["markdown.gh"] = "GH ",
      }

      icons.diagnostics = {
        Error = "E ",
        Warn = "W ",
        Hint = "H ",
        Info = "I ",
      }

      icons.git = {
        added = "+ ",
        modified = "~ ",
        removed = "- ",
      }

      icons.dap = {
        Stopped = { "-> ", "DiagnosticWarn", "DapStoppedLine" },
        Breakpoint = "B ",
        BreakpointCondition = "C ",
        BreakpointRejected = "R ",
        LogPoint = "L ",
      }

      icons.kinds = {
        Array = "",
        Boolean = "",
        Class = "",
        Codeium = "",
        Color = "",
        Control = "",
        Collapsed = "> ",
        Constant = "",
        Constructor = "",
        Copilot = "AI ",
        Enum = "",
        EnumMember = "",
        Event = "",
        Field = "",
        File = "",
        Folder = "",
        Function = "",
        Interface = "",
        Key = "",
        Keyword = "",
        Method = "",
        Module = "",
        Namespace = "",
        Null = "",
        Number = "",
        Object = "",
        Operator = "",
        Package = "",
        Property = "",
        Reference = "",
        Snippet = "",
        String = "",
        Struct = "",
        Supermaven = "AI ",
        TabNine = "AI ",
        Text = "",
        TypeParameter = "",
        Unit = "",
        Value = "",
        Variable = "",
      }

      return opts
    end,
  },

  -- Remove LazyVim's hard-coded Nerd Font glyphs from lualine.
  {
    "nvim-lualine/lualine.nvim",
    opts = function(_, opts)
      for _, section in pairs(opts.sections or {}) do
        for _, component in ipairs(section) do
          if type(component) == "table" and component[1] == "filetype" then
            component.icon_only = false
          end
        end
      end

      if opts.sections and opts.sections.lualine_x then
        local icons = LazyVim.config.icons
        opts.sections.lualine_x = {
          Snacks.profiler.status(),
          {
            require("lazy.status").updates,
            cond = require("lazy.status").has_updates,
            color = function()
              return { fg = Snacks.util.color("Special") }
            end,
          },
          {
            "diff",
            symbols = {
              added = icons.git.added,
              modified = icons.git.modified,
              removed = icons.git.removed,
            },
            source = function()
              local gitsigns = vim.b.gitsigns_status_dict
              if gitsigns then
                return {
                  added = gitsigns.added,
                  modified = gitsigns.changed,
                  removed = gitsigns.removed,
                }
              end
            end,
          },
        }
      end

      if opts.sections and opts.sections.lualine_z then
        opts.sections.lualine_z = {
          function()
            return os.date("%R")
          end,
        }
      end

      return opts
    end,
  },

  -- Dashboard shortcuts are text-only without Nerd Font glyphs.
  {
    "folke/snacks.nvim",
    opts = {
      dashboard = {
        preset = {
          keys = {
            { icon = "", key = "f", desc = "Find File", action = ":lua Snacks.dashboard.pick('files')" },
            { icon = "", key = "n", desc = "New File", action = ":ene | startinsert" },
            { icon = "", key = "g", desc = "Find Text", action = ":lua Snacks.dashboard.pick('live_grep')" },
            { icon = "", key = "r", desc = "Recent Files", action = ":lua Snacks.dashboard.pick('oldfiles')" },
            { icon = "", key = "c", desc = "Config", action = ":lua Snacks.dashboard.pick('files', { cwd = vim.fn.stdpath('config') })" },
            { icon = "", key = "s", desc = "Restore Session", section = "session" },
            { icon = "", key = "x", desc = "Lazy Extras", action = ":LazyExtras" },
            { icon = "", key = "l", desc = "Lazy", action = ":Lazy" },
            { icon = "", key = "q", desc = "Quit", action = ":qa" },
          },
        },
      },
    },
  },
}
