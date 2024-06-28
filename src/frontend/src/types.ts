export interface NavigationData {
    id: number,
    imageSrc: string,
    label: string,
    isActive: boolean
}

export enum Access {
    Bid,
		Budget
}

export interface PanelData extends NavigationData {
    panel: any,
    access: Access
}
