**Feedback API**
- When Ride Admin Clicks on mark as completed, every passenger gets the form of writing Feedback which is savedSafety, Comfort, Punctuality

API endpoint
post 
{
    MemberID,
    RideID,
    FeedbackText,
    FeedbackCategory,
    [ReceiverMemberID, Rating, RatingComment]
}

This adds rows in RideFeedback table and MemberRating table
class MemberRating(Base):
    __tablename__ = "MemberRatings"

    RideID = Column(String(50), primary_key=True)
    SenderMemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    ReceiverMemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Rating = Column(Float, nullable=False)
    RatingComment = Column(String(500))
    RatedAt = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)
class RideFeedback(Base):
    __tablename__ = "RideFeedback"

    RideID = Column(String(50), primary_key=True)
    MemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    FeedbackText = Column(String(500), nullable=False)
    FeedbackCategory = Column(String(50))
    SubmittedAt = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

It would also change member stat table since ride hosted and trip taken increases and ratings also changes
class MemberStat(Base):
    __tablename__ = "MemberStats"

    MemberID = Column(Integer, ForeignKey("Members.MemberID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    AverageRating = Column(Float, nullable=False, default=0.00)
    TotalRidesTaken = Column(Integer, nullable=False, default=0)
    TotalRidesHosted = Column(Integer, nullable=False, default=0)
    NumberOfRatings = Column(Integer, nullable=False, default=0)

I think clicking on markascompleted doesn't change delete ride directly after filling this type of form it will change