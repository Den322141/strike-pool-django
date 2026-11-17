from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ICONS = {
    'bowling': '<svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <circle cx="12" cy="12" r="10"></circle>\n        <circle cx="9" cy="9" r="1.5" fill="currentColor"></circle>\n        <circle cx="15" cy="9" r="1.5" fill="currentColor"></circle>\n        <circle cx="12" cy="14" r="1.5" fill="currentColor"></circle>\n    </svg>',
    'billiards': '<svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <circle cx="12" cy="12" r="10"></circle>\n        <path d="M12 7a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>\n        <path d="M12 11a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z"></path>\n    </svg>',
    'pool': '<svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <rect x="2" y="5" width="20" height="14" rx="3"></rect>\n        <circle cx="6" cy="9" r="1.2" fill="currentColor"></circle>\n        <circle cx="18" cy="9" r="1.2" fill="currentColor"></circle>\n        <circle cx="6" cy="15" r="1.2" fill="currentColor"></circle>\n        <circle cx="18" cy="15" r="1.2" fill="currentColor"></circle>\n        <circle cx="12" cy="12" r="2.5"></circle>\n    </svg>',
    'cocktail': '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <path d="M8 22h8"></path>\n        <path d="M12 15v7"></path>\n        <path d="m3 3 9 9 9-9z"></path>\n    </svg>',
    'users': '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>\n        <circle cx="9" cy="7" r="4"></circle>\n        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>\n        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>\n    </svg>',
    'calendar': '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>\n        <line x1="16" y1="2" x2="16" y2="6"></line>\n        <line x1="8" y1="2" x2="8" y2="6"></line>\n        <line x1="3" y1="10" x2="21" y2="10"></line>\n    </svg>',
    'clock': '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <circle cx="12" cy="12" r="10"></circle>\n        <polyline points="12 6 12 12 16 14"></polyline>\n    </svg>',
    'card': '<svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">\n        <rect x="2" y="5" width="20" height="14" rx="2"></rect>\n        <line x1="2" y1="10" x2="22" y2="10"></line>\n    </svg>',
}


@register.simple_tag
def icon(name):
    return mark_safe(ICONS.get(name, ""))
