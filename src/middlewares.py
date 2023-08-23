import logging

debugger = logging.getLogger('debugger')


# class QueryLoggingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(
#         self, request: Request, call_next,
#     ) -> Response:
#         if not config('DEBUG', False):
#             return await call_next(request)
#
#         async with async_session_maker() as session:
#
#             request.state.db = session
#             response = await call_next(request)
#
#             queries = getattr(request.state.db, 'queries', [])
#             for query in queries:
#                 debugger.debug(f'Executed query: {query[0]} with parameters: {query[1]}')
#
#             debugger.debug('Total queries executed: %d', len(queries))
#
#             await session.close()
#
#             return response
