import { Access, PanelData } from "@/types"
import BidPanel from "./BidPanel.vue"

const panels: Array<PanelData> = [
    {
        panel: BidPanel,
        access: Access.Bid
    },
]

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
    const result: Array<PanelData> = []

    for (let i = 0; i < accesses.length; i++) {
        const access = accesses[i];
        
        for (let j = 0; j < panels.length; j++) {
            const panel = panels[j];
            
            if (panel.access === access)
							result.push(panel)
        }
    }

		return result
}
