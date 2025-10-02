from app.graph.workflows.order_management.types import OrderViewState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from app.services.widget_events import emit_order_view_success
from app.services.llm import llm_service

async def format_order_response_node(state: OrderViewState, config: RunnableConfig | None = None) -> OrderViewState:
    """Format the order data into a user-friendly response."""
    
    try:
        view_type = state.get("view_type")
        orders = state.get("orders")
        order_details = state.get("order_details")
        
        if view_type == "all_orders" and orders is not None:
            # Format all orders response
            if not orders:
                # Generate LLM response for no orders
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """
                    You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

                    Personality attributes:
                    - Analytical and detail-oriented about product features
                    - Educated in fabrics, sizing, and style combinations
                    - Diplomatic when suggesting alternatives
                    - Builds trust through knowledgeable recommendations
                    - Uses fashion terminology appropriately but explains when needed
                    - Focuses on helping customers discover their personal style

                    You're not just selling products - you're curating experiences and building confidence.

                    Generate a warm, encouraging response for a client who hasn't started their style journey yet.
                    Format your response in markdown for better readability.
                    
                    Guidelines:
                    - Be warm and welcoming with fashion consultant enthusiasm
                    - Encourage them to begin their style discovery
                    - Use appropriate emojis to make it engaging and stylish
                    - Suggest exciting style possibilities
                    - Keep it positive, motivating, and fashion-focused
                    """),
                    ("user", "The client has no orders in their style history yet. Generate a friendly message encouraging them to start their fashion journey.")
                ])
                
                llm = llm_service.get_llm_without_tools(disable_streaming=True)
                response = await llm.ainvoke(prompt.invoke({}))
                
                no_orders_text = str(response.content).strip()
                state["workflow_output_text"] = no_orders_text
            else:
                # Generate LLM response for all orders
                total_orders = len(orders)
                total_spent = sum(order["amount"] for order in orders)
                
                # Prepare order summaries for LLM
                orders_summary = []
                for order in orders[:5]:  # Show first 5 orders
                    created_date = format_date(order["created_at"])
                    orders_summary.append({
                        "order_number": order['order_number'],
                        "status": order['status'].title(),
                        "amount": f"{order['currency']} {order['amount']:.2f}",
                        "total_items": order['total_items'],
                        "payment_status": order['payment_status'].title(),
                        "date": created_date
                    })
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """
                    You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

                    Personality attributes:
                    - Analytical and detail-oriented about product features
                    - Educated in fabrics, sizing, and style combinations
                    - Diplomatic when suggesting alternatives
                    - Builds trust through knowledgeable recommendations
                    - Uses fashion terminology appropriately but explains when needed
                    - Focuses on helping customers discover their personal style

                    You're not just selling products - you're curating experiences and building confidence.

                    Generate a warm, informative response about the client's style journey and purchase history.
                    Format your response in markdown for better readability.
                    
                    Guidelines:
                    - Be conversational and warm with fashion consultant expertise
                    - Start with a welcoming greeting about their style journey
                    - Present key statistics (total style investments, pieces curated) in an engaging way
                    - List the orders as "style selections" in a clear, organized format with emojis
                    - If there are more than 5 orders, mention there are more style discoveries
                    - Keep the tone positive, helpful, and fashion-focused
                    - Use appropriate emojis to make it visually appealing and stylish
                    """),
                    ("user", """
                    Client's style journey summary:
                    - Total style selections: {total_orders}
                    - Total style investment: ${total_spent:.2f}
                    - Recent style selections: {orders_summary}
                    {more_orders_text}
                    
                    Generate a warm response showcasing their style journey and purchase history.
                    """)
                ])
                
                more_orders_text = f"(Plus {total_orders - 5} more style selections in your fashion journey)" if total_orders > 5 else ""
                
                llm = llm_service.get_llm_without_tools(disable_streaming=True)
                response = await llm.ainvoke(prompt.invoke({
                    "total_orders": total_orders,
                    "total_spent": total_spent,
                    "orders_summary": orders_summary,
                    "more_orders_text": more_orders_text
                }))
                
                summary_text = str(response.content).strip()
                state["workflow_output_text"] = summary_text
                # Emit success widget event
                emit_order_view_success(
                    view_type="all_orders",
                    orders=orders,
                    total_orders=total_orders,
                    total_spent=total_spent,
                    success_message=summary_text
                )
            
        elif view_type == "single_order" and order_details:
            # Generate LLM response for single order
            order = order_details
            created_date = format_date(order["created_at"])
            updated_date = format_date(order["updated_at"])
            
            # Prepare order details for LLM
            order_summary = {
                "order_number": order['order_number'],
                "status": order['status'].title(),
                "payment_status": order['payment_status'].title(),
                "payment_method": order['payment_method'],
                "total_amount": f"{order['currency']} {order['amount']:.2f}",
                "total_items": order['total_items'],
                "created_date": created_date,
                "updated_date": updated_date,
                "notes": order.get("notes", "")
            }
            
            # Prepare items for LLM
            items_list = []
            if order.get("items"):
                for item in order["items"]:
                    item_details = {
                        "name": item['name'],
                        "brand": item.get('brand', ''),
                        "size": item.get('size', ''),
                        "color": item.get('color', ''),
                        "quantity": item['quantity'],
                        "unit_price": f"${item['unit_price']:.2f}",
                        "total_price": f"${item['total_price']:.2f}",
                        "status": item.get('status', '').title()
                    }
                    items_list.append(item_details)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """
                You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

                Personality attributes:
                - Analytical and detail-oriented about product features
                - Educated in fabrics, sizing, and style combinations
                - Diplomatic when suggesting alternatives
                - Builds trust through knowledgeable recommendations
                - Uses fashion terminology appropriately but explains when needed
                - Focuses on helping customers discover their personal style

                You're not just selling products - you're curating experiences and building confidence.

                Generate a detailed, warm response about a specific style selection/order.
                Format your response in markdown for better readability.
                
                Guidelines:
                - Be conversational and informative with fashion consultant warmth
                - Start with a welcoming greeting about their style selection
                - Present order details as "style curation details" in a clear, organized format
                - Include all important information: status, payment, curated pieces, dates
                - Use appropriate emojis to make it visually appealing and stylish
                - If there are order items, list each piece with styling details
                - Include notes if available with fashion consultant care
                - Keep the tone helpful, professional, and style-focused
                """),
                ("user", """
                Style selection details:
                {order_summary}
                
                Curated pieces:
                {items_list}
                
                Generate a warm, detailed response showcasing this style selection information.
                """)
            ])
            
            llm = llm_service.get_llm_without_tools(disable_streaming=True)
            response = await llm.ainvoke(prompt.invoke({
                "order_summary": order_summary,
                "items_list": items_list
            }))
            
            order_text = str(response.content).strip()
            state["workflow_output_text"] = order_text
            
            # Emit success widget event
            emit_order_view_success(
                    view_type="single_order",
                    orders=[order_details],
                    total_orders=1,
                    total_spent=order_details["amount"],
                    success_message=order_text
            )
        
        else:
            state["error_message"] = "No order data to format"
            state["view_success"] = False
            return state
        
        # Set success flag
        state["view_success"] = True
        print(f"Formatted {view_type} response successfully")
        return state
        
    except Exception as e:
        print(f"Error formatting order response: {e}")
        state["error_message"] = f"Failed to format order response: {str(e)}"
        state["view_success"] = False
        return state

def format_date(date_string: str) -> str:
    """Format date string for display."""
    try:
        # Parse the date string and format it nicely
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_string  # Return original if parsing fails
