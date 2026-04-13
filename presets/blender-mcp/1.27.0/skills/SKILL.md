---
name: "blender-mcp"
description: Control Blender scenes, execute Python code, and import 3D assets from PolyHaven/Sketchfab/Hyper3D/Hunyuan3D via CLI. Use when user needs to manipulate Blender objects, generate AI 3D models, or apply textures.
source_version: "1.27.0"
source_cli_hash: "38cd7cf1"
generated_at: "2026-04-06T08:56:37.438688+00:00"
---

# blender-mcp (via mcp2cli)

Control Blender and import 3D assets via CLI.

## Shortcuts

- `mcp2cli blender <cmd>` (alias for `mcp2cli blender-mcp`)

## Commands

### Scene
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender scene get` | Get current scene info | `mcp2cli blender scene get --user-prompt 'show scene'` | [ref](reference/scene.md) |
| `mcp2cli blender scene object get` | Get object details | `mcp2cli blender scene object get --object-name Cube` | [ref](reference/scene.md) |
| `mcp2cli blender scene viewport screenshot` | Capture viewport screenshot | `mcp2cli blender scene viewport screenshot --max-size 1200` | [ref](reference/scene.md) |

### Code
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender code execute` | Execute Python code in Blender | `mcp2cli blender code execute --code 'bpy.ops.mesh.primitive_cube_add()'` | [ref](reference/code.md) |

### PolyHaven
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender polyhaven asset search` | Search PolyHaven assets | `mcp2cli blender polyhaven asset search --asset-type textures` | [ref](reference/polyhaven.md) |
| `mcp2cli blender polyhaven asset download` | Download and import asset | `mcp2cli blender polyhaven asset download --asset-id venice-sunset --asset-type hdris --resolution 2k` | [ref](reference/polyhaven.md) |
| `mcp2cli blender polyhaven texture set` | Apply texture to object | `mcp2cli blender polyhaven texture set --object-name Cube --texture-id wood-plank` | [ref](reference/polyhaven.md) |
| `mcp2cli blender polyhaven category list` | List asset categories | `mcp2cli blender polyhaven category list --asset-type textures` | [ref](reference/polyhaven.md) |

### Sketchfab
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender sketchfab model search` | Search Sketchfab models | `mcp2cli blender sketchfab model search --query 'wooden chair'` | [ref](reference/sketchfab.md) |
| `mcp2cli blender sketchfab model preview` | Preview model thumbnail | `mcp2cli blender sketchfab model preview --uid abc123` | [ref](reference/sketchfab.md) |
| `mcp2cli blender sketchfab model download` | Download and import model | `mcp2cli blender sketchfab model download --uid abc123 --target-size 1.0` | [ref](reference/sketchfab.md) |

### Hyper3D
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender hyper3d model generate-from-text` | Generate 3D model from text | `mcp2cli blender hyper3d model generate-from-text --text-prompt 'a wooden barrel'` | [ref](reference/hyper3d.md) |
| `mcp2cli blender hyper3d model generate-from-images` | Generate 3D model from images | | [ref](reference/hyper3d.md) |
| `mcp2cli blender hyper3d model import` | Import generated Hyper3D asset | `mcp2cli blender hyper3d model import --name MyModel --task-uuid abc123` | [ref](reference/hyper3d.md) |
| `mcp2cli blender hyper3d job poll` | Poll Hyper3D job status | | [ref](reference/hyper3d.md) |

### Hunyuan3D
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli blender hunyuan3d model generate` | Generate 3D model (text/image) | `mcp2cli blender hunyuan3d model generate --text-prompt 'a ceramic vase'` | [ref](reference/hunyuan3d.md) |
| `mcp2cli blender hunyuan3d model import` | Import generated Hunyuan3D asset | `mcp2cli blender hunyuan3d model import --name MyModel --zip-file-url /path/model.zip` | [ref](reference/hunyuan3d.md) |
| `mcp2cli blender hunyuan3d job poll` | Poll Hunyuan3D job status | | [ref](reference/hunyuan3d.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli blender code execute --help

> **Note**: Use Ref links above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
