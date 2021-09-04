-- name: get_overall_status
with recursive tds_children as (
    select id,
           parent_id,
           todo,
           metadata,
           tags,
           desc,
           path,
           flags,
           last_update_ts,
           created_at,
           0 as depth
    from vimtool_todos
    where id == :id_
      and flags <= 4
    union all
    select vimtool_todos.id,
           vimtool_todos.parent_id,
           vimtool_todos.todo,
           vimtool_todos.metadata,
           vimtool_todos.tags,
           vimtool_todos.desc,
           vimtool_todos.path,
           vimtool_todos.flags,
           vimtool_todos.last_update_ts,
           vimtool_todos.created_at,
           tds_children.depth + 1
    from vimtool_todos
             join tds_children
    where vimtool_todos.parent_id == tds_children.id
      and vimtool_todos.flags <= 4
)
select min(flags) overall_status
from tds_children
where id != :id_
--where level < 3  -- only one level down
;

-- name: get_todo_parent
-- record_class: Todo
with recursive tds_parents as (
    select id,
           parent_id,
           todo,
           metadata,
           tags,
           desc,
           path,
           flags,
           last_update_ts,
           created_at,
           0 as depth
    from vimtool_todos
    where id = :id_
      and flags <= 4
    union all
    select vimtool_todos.id,
           vimtool_todos.parent_id,
           vimtool_todos.todo,
           vimtool_todos.metadata,
           vimtool_todos.tags,
           vimtool_todos.desc,
           vimtool_todos.path,
           vimtool_todos.flags,
           vimtool_todos.last_update_ts,
           vimtool_todos.created_at,
           tds_parents.depth - 1
    from vimtool_todos
             join tds_parents
    where vimtool_todos.id == tds_parents.parent_id
      and vimtool_todos.flags <= 4
)
select *
from tds_parents
where depth = :depth
;


-- name: get_depth
with recursive tds_parents as (
    select id, parent_id, todo, 0 as depth
    from vimtool_todos
    where id == :id_
      and flags <= 4
    union all
    select vimtool_todos.id, vimtool_todos.parent_id, vimtool_todos.todo, tds_parents.depth - 1
    from vimtool_todos
             join tds_parents
    where vimtool_todos.id == tds_parents.parent_id
      and vimtool_todos.flags < 4
)
select depth
from tds_parents
order by depth
limit 1
;
