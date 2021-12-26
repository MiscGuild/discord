from __main__ import bot

async def get_graph_color_by_rank(rank: str, weekly_gexp: int):
    if rank == "Resident":
        # Member meets res reqs
        if weekly_gexp > bot.resident_req:
            return 0x64ffb4, 'rgba(100, 255, 180,0.3)', 'rgba(100, 255, 180,0.3)'

        # Member does not meet res reqs
        return 0xffb464, 'rgba(255, 180, 100,0.3)', 'rgba(255, 180, 100,0.3)'
    
    else:
        # Member meets active reqs
        if weekly_gexp > bot.active_req:
            return 0x64b4ff, 'rgba(100, 180, 255,0.3)', 'rgba(100, 180, 255,0.3)'

        # Member meets normal reqs
        if weekly_gexp > bot.member_req:
            return 0x64ffff, 'rgba(100, 255, 255,0.3)', 'rgba(100, 255, 255,0.3)'
        
        # Member is inactive
        return 0xff6464, 'rgba(255, 100, 100,0.3)', 'rgba(255, 100, 100,0.3)'
