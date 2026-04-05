# Diagram Commands

## create — Create a new diagram from mxGraphModel XML

```bash
# Create a simple diagram with one shape
mcp2cli next-ai-draw-io diagram create --xml '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="Start" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="100" y="100" width="120" height="60" as="geometry"/></mxCell></root></mxGraphModel>'

# Create a flowchart with edges
mcp2cli next-ai-draw-io diagram create --xml '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="A" vertex="1" parent="1"><mxGeometry x="100" y="100" width="120" height="60" as="geometry"/></mxCell><mxCell id="3" value="B" vertex="1" parent="1"><mxGeometry x="300" y="100" width="120" height="60" as="geometry"/></mxCell><mxCell id="4" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell></root></mxGraphModel>'
```

Required: `--xml` (complete mxGraphModel XML)

> Use this for new diagrams or full replacement. For small changes, use `diagram edit`.

## get — Get the current diagram XML

```bash
mcp2cli next-ai-draw-io diagram get
```

Fetches latest XML from browser including any manual user edits. ⚠️ Always call BEFORE `diagram edit` to get current cell IDs.

## edit — Edit diagram by ID-based cell operations

```bash
# Add a new cell
mcp2cli next-ai-draw-io diagram edit --operations '[{"operation":"add","cell_id":"rect-1","new_xml":"<mxCell id=\"rect-1\" value=\"Hello\" style=\"rounded=0;\" vertex=\"1\" parent=\"1\"><mxGeometry x=\"100\" y=\"100\" width=\"120\" height=\"60\" as=\"geometry\"/></mxCell>"}]'

# Update a cell label
mcp2cli next-ai-draw-io diagram edit --operations '[{"operation":"update","cell_id":"2","new_xml":"<mxCell id=\"2\" value=\"New Label\" style=\"rounded=1;\" vertex=\"1\" parent=\"1\"><mxGeometry x=\"100\" y=\"100\" width=\"120\" height=\"60\" as=\"geometry\"/></mxCell>"}]'

# Delete a cell
mcp2cli next-ai-draw-io diagram edit --operations '[{"operation":"delete","cell_id":"rect-1"}]'
```

Required: `--operations` (JSON array of operations)

Each operation requires: `operation` (add/update/delete), `cell_id`. Add/update also require `new_xml` (complete mxCell element).

⚠️ **Workflow**: call `diagram get` first → use returned IDs in operations.

## download — Export the current diagram to a file

```bash
# Export as PNG
mcp2cli next-ai-draw-io diagram download --path ./diagram.png

# Export as SVG
mcp2cli next-ai-draw-io diagram download --path ./diagram.svg --format svg

# Export as drawio XML
mcp2cli next-ai-draw-io diagram download --path ./diagram.drawio --format drawio
```

Required: `--path`

Also supports: `--format` (drawio | png | svg; auto-detected from extension if omitted)

Use `mcp2cli next-ai-draw-io diagram <action> --help` for full parameter details.
