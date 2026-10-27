' Sample.vb -- synthetic fixture exercising VB.NET structural edge cases.
' The real benchmark files (Track.vb, Signal.vb, AdministrativeEvent.vb) are not
' in this repository; see design/deterministic-source-layer/.

Imports System

Namespace Dispatch

    ''' <summary>Track status values.</summary>
    Public Enum StateOfOnBoard As Integer
        Inactive = 0
        Active = 1
        InactiveLoggedOn = 2
    End Enum

    Public Interface ITrackSource
        Function GetId() As Integer
        Sub Refresh()
        Property Label As String
    End Interface

    Public Class Track
        Implements ITrackSource

#Region "Fields"
        Private _id As Integer
        ' A string containing keywords that must NOT be parsed as structure:
        Private _trap As String = "End Class Public Function Fake() #Region"
        Private Const BANNER As String = "Sub Main() ' not a comment"
#End Region

#Region "Members"

        Public Sub New()
            _id = 0
        End Sub

        ' Auto-implemented property: no End Property.
        Public Property Label As String Implements ITrackSource.Label

        ' Block property: has accessors.
        Public Property Id As Integer
            Get
                Return _id
            End Get
            Set(value As Integer)
                _id = value
            End Set
        End Property

        Public Function GetId() As Integer Implements ITrackSource.GetId
            Return _id   ' REM-like text: not a REM comment
            REM this IS a rem comment
        End Function

        Public Sub Refresh() Implements ITrackSource.Refresh
            If _id > 0 AndAlso Not String.IsNullOrEmpty(Label) Then
                Console.WriteLine("Refreshing")
            End If
        End Sub

        Public Sub TrackTrainIDOn(ByVal trainId As Integer, _
                                  ByVal force As Boolean)
            Select Case trainId
                Case 0
                    Return
                Case Else
                    _id = trainId
            End Select
        End Sub

        Private Declare Function GetTickCount Lib "kernel32" () As Integer

        Public MustOverride Sub AbstractOp()

        Public Event Changed As EventHandler

#End Region

    End Class

    Public Module Helpers
        Public Function Describe(ByVal t As Track) As String
            Return t.Label
        End Function
    End Module

End Namespace
