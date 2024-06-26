export interface NavigationButton {
    id: number,
    imageSrc: string,
    label: string,
    isActive: boolean
}

export enum Access {
    Bid,
}

export interface PanelData {
    panel: any,
    access: Access
}