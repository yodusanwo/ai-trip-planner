# We Created Our First Multi-Agent AI Tool: Lessons from Building a Travel Planning Agent

We created our first multi-agent AI tool as a simple showcase of AI Agent capabilities. This tool has three agents that leverage the GPT-4o-mini model to create personalized travel itineraries. Here are the top 15 things I learned from building this Travel Planning Agent:

## 1. Clear Prompts Are Everything

The most critical lesson: **prompt engineering makes or breaks your agent's performance**. We spent significant time refining instructions for each agent:

- **The Researcher** needs explicit pricing rules, data collection guidelines, and verification requirements
- **The Reviewer** requires clear validation criteria, content filters, and formatting standards
- **The Planner** must have detailed HTML structure requirements, brand styling guidelines, and hyperlink rules

Without crystal-clear prompts, agents would produce inconsistent outputs, miss critical details, generate reference messages instead of actual content, or even hallucinate fake places. We learned to be explicit about:

- Expected output formats
- Required sections and structure
- Brand guidelines (colors, styling)
- Budget constraints and pricing rules
- Verification requirements (no hallucinations)
- Content safety filters
- What NOT to do (e.g., "Do NOT write 'see HTML document above'", "Do NOT invent restaurant names")

**Takeaway:** Invest time upfront in prompt engineering. It saves hours of debugging later and prevents embarrassing hallucinations.

**Prompt Length Management:** We learned to balance detail with brevity. Our current prompts total ~6,700 characters across all three tasks (Research: ~3,900, Review: ~1,000, Planning: ~1,800). While comprehensive prompts are essential for accuracy, excessively long prompts can:

- Increase token costs
- Slow down processing
- Make it harder for agents to focus on key requirements
- Risk hitting context limits

We found the sweet spot: detailed enough to prevent hallucinations, concise enough to remain focused. Regular refactoring helps maintain this balance.

## 2. Multi-Language Deployment: Backend + Frontend

We deployed a **Python FastAPI backend** on Railway and a **Next.js TypeScript frontend** on Vercel. This taught us:

- **Environment Variables:** Managing different configs for dev/staging/production across platforms
- **CORS Configuration:** Ensuring the frontend can communicate with the backend
- **API Design:** Creating RESTful endpoints that work seamlessly with React components
- **Deployment Workflows:** Understanding how each platform builds and deploys different tech stacks

The separation of concerns (Python for AI logic, TypeScript for UI) worked beautifully, but required careful coordination of environment variables and API contracts.

## 3. Agent Orchestration Requires Sequential Thinking

Our three-agent workflow follows a **sequential process**:

1. **Researcher** → Gathers destination data, pricing, attractions (with verification)
2. **Reviewer** → Validates, filters inappropriate content, verifies all locations
3. **Planner** → Creates the final HTML itinerary with verified hyperlinks

We learned that agents need clear handoff points. The Reviewer's output must be perfectly formatted and verified for the Planner to consume. This required us to:

- Define expected output formats for each stage
- Ensure data consistency between agents
- Handle edge cases where research might be incomplete
- Build verification steps into each handoff (no unverified data passes through)

## 4. Real-World Constraints Matter (Especially Pricing)

One of our biggest challenges: **getting realistic accommodation pricing**. The AI would suggest $30/night hotels in Paris, which don't exist. We solved this by:

- Creating city-specific minimum pricing rules
- Enforcing budget ranges (e.g., Paris: $150–$220/night for moderate)
- Adding validation steps in the Reviewer agent
- Expressing costs as ranges, not single numbers

This taught us that AI agents need guardrails for real-world constraints. Without them, outputs can be technically correct but practically useless.

## 5. HTML Generation Requires Explicit Structure

The Planner agent generates complete HTML documents. We learned that:

- **Structure matters:** Providing exact HTML templates ensures consistency
- **Styling is critical:** Inline CSS with brand colors must be mandatory
- **Validation is essential:** We check for HTML tags, not just text content
- **Complete output required:** Agents sometimes return references instead of actual HTML—this needs explicit prevention

We ended up including a complete HTML template in the prompt, showing exactly what tags to use and where.

## 6. Error Handling Across the Stack

We encountered several deployment issues:

- **Module import errors** (missing `src` directory structure)
- **Docker build failures** (incorrect file paths)
- **PDF generation crashes** (WeasyPrint dependencies)
- **CORS errors** (frontend-backend communication)

Each error taught us to:

- Test locally before deploying
- Use proper Docker build contexts
- Handle binary data correctly (PDF downloads)
- Configure CORS properly for production

## 7. Rate Limiting and Security

We implemented rate limiting to control API costs:

- Hourly limits (5 trips/hour)
- Daily limits (5 trips/day)
- Cost-based caps ($2.50/day)
- Per-client tracking using client IDs

This taught us that AI tools need cost controls from day one. Without limits, usage can spiral quickly.

## 8. Real-Time Progress Updates with Server-Sent Events

We implemented **Server-Sent Events (SSE)** to show real-time progress:

- Users see which agent is working
- Progress updates stream from backend to frontend
- Better UX than polling or waiting blindly

This required:

- Proper SSE implementation in FastAPI
- React hooks to consume the event stream
- Error handling for connection drops
- Clean state management

## 9. PDF Generation Adds Complexity

Converting HTML to PDF using WeasyPrint required:

- System dependencies (Cairo, Pango, GDK)
- Proper Docker configuration
- Binary data handling in API responses
- Correct HTTP headers for file downloads

We learned that PDF generation is more complex than expected, especially with styling and layout requirements.

## 10. Content Safety and Verification Are Non-Negotiable

As we refined the tool, we added critical safeguards:

- **Inappropriate Content Filters:** Explicit rules to prevent illegal, explicit, or harmful content
- **Location Verification:** Every restaurant, attraction, and activity must be verified via Google Maps or official websites
- **Anti-Hallucination Measures:** Agents are instructed NOT to invent place names or details
- **Hyperlink Enforcement:** All verified locations must include working hyperlinks in the final HTML
- **Hard Address Verification:** Addresses must be copied verbatim from sources—no rewriting, translation, or inference allowed
- **Exact City + Country Matching:** Strict validation that every location matches the destination city AND country exactly
- **Branch Handling:** Rules for multi-location businesses to ensure the correct branch is selected
- **Re-Verification:** Reviewer agent performs fresh searches to confirm every location before passing to planner
- **Intelligent Evaluation:** Agents go beyond basic search—they analyze comments, ratings, and reviews from real users to make quality recommendations. This adds intelligence to the search process by leveraging collective feedback from others who have visited these places

**Beyond Basic Search: Intelligent Recommendation Evaluation**

What sets our agents apart from simple search tools is their ability to **evaluate and synthesize user feedback**. When researching restaurants, attractions, or activities, our agents don't just find places—they:

- **Review ratings and reviews** from platforms like Google Maps, TripAdvisor, and Yelp
- **Analyze comments** to understand what makes a place special or identify potential issues
- **Consider user feedback patterns** to distinguish between consistently praised venues and those with mixed reviews
- **Make informed recommendations** based on aggregated intelligence from hundreds or thousands of previous visitors

This goes beyond basic search because it adds **intelligence and context** to recommendations. Instead of just returning a list of places, the agents evaluate quality signals from real user experiences. For example, a restaurant might appear in search results, but if reviews consistently mention poor service or food quality, the agent can factor that into its recommendation—or exclude it entirely.

This evaluation process ensures that recommendations aren't just verified to exist, but are also **validated for quality** based on the collective wisdom of previous visitors. It's the difference between "here's a restaurant" and "here's a restaurant that people consistently love."

We learned that AI agents can hallucinate restaurant names, create fake attractions, suggest places that don't exist, or even modify addresses incorrectly. Our solution evolved to be increasingly strict:

- Require verification via SerperDevTool searches
- Enforce that every recommended place has a valid URL
- Remove or replace unverified locations in the review stage
- Use Google Maps URLs for restaurants/cafés, official sites for attractions
- **Copy addresses verbatim** from verified sources—no modification allowed
- **Re-verify every location** with fresh searches in the review stage
- **Reject ambiguous results** that could match multiple cities or countries

**Takeaway:** Trust but verify—and verify again. Address accuracy matters just as much as location existence. Always build multiple verification layers into your agent workflows, and never allow agents to modify verified data.

## 11. Version Control and Deployment Workflow

Managing deployments across multiple platforms taught us:

- **Git branching strategy:** Feature branches → main → auto-deploy
- **Environment parity:** Dev, staging, production configs
- **Rollback procedures:** How to quickly revert bad deployments
- **Monitoring:** Checking logs on Railway and Vercel

We also learned to never commit `.env` files (GitHub's secret scanning caught us!).

## 12. Automated Validation Catches What Prompts Miss

Even with the best prompts, agents can still make mistakes. We learned to add **automated validation** as a safety net:

- **Post-Processing Validation:** After the crew completes, we run `validate_itinerary_output()` to check for:

  - Repeated restaurants across different days
  - Repeated activities (unless intentional)
  - Multiple accommodations when one should be selected
  - Inconsistent hotel options format

- **Non-Blocking Warnings:** Validation runs automatically but doesn't block the request—it logs warnings for monitoring. This gives us visibility into quality issues without impacting user experience.

- **Pattern Matching:** We use regex patterns to detect common issues that prompts alone can't prevent, like agents repeating the same restaurant name across multiple days.

**Takeaway:** Prompts guide behavior, but validation catches edge cases. Combine both for the best results. Our validation function runs automatically on every itinerary, providing continuous quality monitoring.

## 13. Development Doesn't Stop at Launch

One of the most important lessons: **launching is just the beginning**. After deployment, we quickly realized that development is an ongoing process:

- **Continuous Testing:** We discovered edge cases in production that never appeared in development (e.g., agents returning reference messages instead of HTML, PDF corruption issues)
- **Iterative Improvements:** We've already made multiple updates post-launch:
  - Added content safety filters
  - Implemented location verification
  - Enhanced hyperlink enforcement
  - Refined pricing rules based on user feedback
  - Streamlined and refactored agent prompts for clarity and maintainability
  - Added hard address verification (verbatim copy requirements)
  - Implemented exact city + country matching rules
  - Enhanced reviewer re-verification process
  - Added automated validation function to check for repeated restaurants/activities and accommodation consistency
  - Integrated validation into production workflow for quality assurance
- **Monitoring and Debugging:** Production logs revealed issues we couldn't predict (hallucinated restaurant names, unrealistic pricing, missing hyperlinks, incorrect addresses, wrong-city results)
- **Feature Evolution:** New requirements emerged after users started using the tool (better verification, brand color consistency, special requirements handling)
- **Code Refactoring:** As we learned more, we refactored the crew configuration to be more concise, focused, and maintainable—reducing complexity while improving accuracy

We learned that:

- **Monitor actively:** Check logs regularly, watch for error patterns, track user feedback
- **Iterate quickly:** Fix issues as they arise, don't wait for a "perfect" version
- **Test continuously:** Production behavior differs from local testing—always verify in the live environment
- **Plan for maintenance:** Budget time for ongoing improvements, not just initial development
- **Refactor regularly:** As you learn what works, simplify and streamline your code—shorter, clearer prompts often work better than verbose ones
- **Be increasingly strict:** As you discover edge cases (wrong addresses, multi-location ambiguity), add stricter rules—it's better to reject uncertain data than to output incorrect information
- **Monitor prompt length:** Keep track of prompt sizes (our current total is ~6,700 characters). Balance detail with brevity—too long and agents lose focus, too short and they miss critical requirements
- **Add automated validation:** Build validation functions to catch issues agents might miss (repeated content, inconsistencies). This provides an extra quality check without relying solely on prompts

**Takeaway:** Building the tool was 30% of the work. Maintaining, testing, and improving it is the other 70%. Embrace continuous improvement as part of the development process. And remember: refactoring for clarity and maintainability is just as important as adding new features.

## 14. Prompt Engineering Takes Just as Long to Perfect After Launch

Here's a reality check: **prompt engineering doesn't end when your code is running**. In fact, we spent as much time refining prompts _after_ deployment as we did building the initial system.

**Why?** Because real-world usage reveals edge cases you never anticipated:

- **Intermittent Issues:** The agent would sometimes return reference messages instead of HTML—only happened in production, not in testing
- **User Feedback:** Users reported two hotel options instead of three, generic descriptions like "explore local art galleries" instead of specific places, and empty departure days
- **Quality Inconsistencies:** Some itineraries were perfect, others had repeated restaurants or missing activities
- **Hallucination Patterns:** We discovered specific hallucination patterns (like "Civilians" restaurant or "1800 Chicago") only after analyzing production outputs

**Our Post-Launch Prompt Refinement Process:**

1. **Monitor Production Outputs:** We analyzed every itinerary generated in production, looking for patterns
2. **Identify Issues:** When users reported problems (generic descriptions, missing hotels, empty days), we traced them back to prompt gaps
3. **Iterate Quickly:** We made prompt changes, tested, deployed, and monitored again—sometimes multiple times per day
4. **Add Validation:** We built automated validation functions to catch issues prompts alone couldn't prevent
5. **Refactor for Clarity:** We streamlined prompts from 609 lines to 231 lines, removing redundancy while preserving critical requirements

**Examples of Post-Launch Prompt Changes:**

- **Hotel Options:** Added explicit requirement for exactly 3 hotels (was allowing 2)
- **Generic Descriptions:** Added forbidden patterns list ("Exploration of the local art galleries" → must use specific gallery names)
- **Departure Day:** Added mandatory morning/afternoon activities requirement (was allowing just "check-out")
- **Blog Link Fallback:** Added curated article link fallback mechanism to prevent generic placeholders
- **Address Verification:** Evolved from "verify addresses" to "copy addresses verbatim—no modification allowed"

**The Iteration Cycle:**

```
Deploy → Monitor → Identify Issue → Refine Prompt → Test → Deploy → Repeat
```

We went through this cycle dozens of times. Each iteration improved quality, but also taught us that:

- **Prompts are living documents:** They need constant refinement based on real-world performance
- **Production is the real test:** Local testing doesn't catch all edge cases
- **User feedback is gold:** Real users find issues you'd never think to test
- **Validation complements prompts:** Automated checks catch what prompts miss
- **Shorter can be better:** We reduced prompt length by 62% while improving accuracy

**Takeaway:** Don't expect your initial prompts to be perfect. Budget significant time for post-launch prompt refinement. The code might be "done," but the prompts are never truly finished—they evolve with every edge case you discover and every user feedback you receive. Prompt engineering is an ongoing process, not a one-time task.

## 15. Integrating Verified APIs: Google Places API for Trustworthy Results

After initial deployment, we realized that **web search alone wasn't enough** for reliable place recommendations. Even with verification steps, we still encountered issues with:

- **Fake or closed businesses** appearing in search results
- **Missing critical information** (addresses, phone numbers, opening hours)
- **Inconsistent data quality** from various web sources
- **Broken or incorrect URLs** that didn't lead to actual businesses

**The Solution: Google Places API Integration**

We integrated Google Places API to replace generic web search with **verified, structured place data**. This was a game-changer for accuracy and trustworthiness.

**What We Gained:**

1. **Verified Business Data:**
   - Real addresses, phone numbers, and websites
   - Google Maps URLs for every place
   - Business status (open/closed/permanently closed)
   - Opening hours and operational status

2. **Quality Metrics:**
   - Star ratings (0-5 scale)
   - Review counts from real users
   - Ability to filter by rating threshold (we reject < 3.5 stars)
   - Automatic rejection of permanently closed businesses

3. **Structured Data:**
   - Consistent data format across all places
   - No more parsing inconsistent web search results
   - Reliable place IDs for follow-up detail requests

4. **Better User Experience:**
   - Direct Google Maps links for navigation
   - Accurate addresses users can trust
   - Phone numbers for making reservations
   - Website links for official information

**Implementation Challenges:**

- **CrewAI Tool Compatibility:** Initially tried using `BaseTool` from `crewai_tools`, but discovered it doesn't exist. Had to refactor to use CrewAI's `@tool` decorator pattern for function-based tools
- **Fallback Strategy:** Made Google Places optional—if API key isn't configured, system falls back to web search. This ensures the app works even without Google Places
- **API Cost Management:** Google Places API has usage limits and costs, so we implemented it as an enhancement rather than a requirement

**The Integration:**

We created three CrewAI tools using the `@tool` decorator:

1. **`google_places_search_tool`**: Search for verified restaurants, attractions, and hotels
2. **`google_place_details_tool`**: Get comprehensive details about specific places
3. **`google_places_autocomplete_tool`**: Help interpret vague destination inputs

**Agent Workflow Updates:**

- **Researcher Agent:** Now prioritizes Google Places API, falls back to web search only for travel blogs
- **Reviewer Agent:** Validates places using Google Places API, rejects low-rated or closed businesses
- **Planner Agent:** Uses Google Maps URLs and verified addresses from Google Places

**Quality Improvements:**

- **Rating Filter:** Automatically rejects places with < 3.5 stars
- **Status Check:** Rejects permanently closed businesses
- **Address Accuracy:** Uses formatted addresses directly from Google (no modification needed)
- **URL Reliability:** All Google Maps URLs are guaranteed to work

**Takeaway:** Integrating verified APIs like Google Places significantly improves data quality and user trust. However, it requires:
- Understanding the API's data structure and limitations
- Building proper fallback mechanisms
- Managing API costs and usage limits
- Adapting to the framework's tool creation patterns (in our case, CrewAI's `@tool` decorator)

The investment in verified APIs pays off in **reduced hallucinations, better user experience, and increased trustworthiness** of recommendations. It's worth the extra complexity for production applications.

## What's Next?

This project was a fantastic learning experience. We're now exploring:

- Adding more agent types (e.g., a Budget Optimizer agent)
- Improving HTML styling and visual design
- Adding user authentication and saved itineraries
- Expanding to more destinations with better pricing data
- Enhancing verification with real-time API checks
- Building a feedback loop to improve location recommendations

## Key Technologies Used

- **Backend:** FastAPI (Python), CrewAI, GPT-4o-mini, WeasyPrint
- **Frontend:** Next.js 14, TypeScript, React, Tailwind CSS
- **Deployment:** Railway (backend), Vercel (frontend)
- **APIs:** Google Places API (verified place data), SerperDevTool (web search fallback)
- **Tools:** Docker, Git, GitHub Actions

## Conclusion

Building a multi-agent AI tool taught us that **simplicity in concept doesn't mean simplicity in execution**. Every component—from prompt engineering to deployment—requires careful thought and iteration. But the result? A working AI travel planner that demonstrates the power of agent orchestration.

The journey from idea to deployment was filled with learning opportunities, and the journey continues as we maintain, test, and improve the tool based on real-world usage. We're excited to apply these lessons to future projects and continue evolving this one.

**Remember:** Launch day isn't the finish line—it's the starting point for continuous improvement.

---

_Have you built a multi-agent AI tool? What were your biggest learnings? Share your thoughts in the comments!_
