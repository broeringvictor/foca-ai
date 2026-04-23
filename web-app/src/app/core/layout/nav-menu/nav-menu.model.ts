export interface NavItem {
  label: string;
  icon?: string;
  route?: string;
  children?: NavItem[];
  sectionLabel?: string;
}

export const NAV_ITEMS: NavItem[] = [
  {
    sectionLabel: 'PRINCIPAL',
    label: 'Anotações',
    icon: 'pi pi-book',
    route: '/study-notes',
  },
  {
    label: 'Estudar',
    icon: 'pi pi-chart-line',
    route: '/study-notes/study',
  },
];
