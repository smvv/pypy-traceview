def group_ir(raw_ir):
    groups = []
    group = []

    for line in raw_ir:
        if line.startswith('debug_merge_point'):
            if group:
                groups.append(group)
            groups.append([line])
            group = []
        else:
            group.append(line)

    if group:
        groups.append(group)

    return groups
