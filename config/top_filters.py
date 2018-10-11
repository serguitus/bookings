from common import filters


class RoomTypeTopFilter(filters.ForeignKeyFilter):

    autocomplete_url = 'roomtype-autocomplete'
