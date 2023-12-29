from chess import Board
import chess
from material_values import *
import numpy as np

# board comes with:
# is_game_over()
# push()
# outcome()
    # return chess.WHITE, chess.BLACK, None (if drawn)

class ChessWrapper(Board):

    # return a list of the legal moves from the current position
    def get_legal_moves(self):
        return list(self.legal_moves)
    
    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        return np.exp(x) / np.sum(np.exp(x), axis=0)

    def eval_legal_moves(self):
        legal_moves = self.get_legal_moves()
        values = []

        for move in legal_moves:
            if self.is_capture(move):

                # attacker's square
                atk_sq = move.from_square
                # defender's square
                def_sq = move.to_square

                atk_piece = self.piece_at(atk_sq)
                def_piece = self.piece_at(def_sq)

                if atk_piece is None or def_piece is None:
                    total_val = 0
                elif atk_piece.piece_type == chess.KING:
                    def_val = BASE_VALUES[def_piece.piece_type]/100
                    total_val = 2 * def_val
                else:
                    # attacker's piece val
                    atk_val = BASE_VALUES[atk_piece.piece_type]/100
                    def_val = BASE_VALUES[def_piece.piece_type]/100

                    # want: use lesser value piece to take greater value piece
                    total_val = 2 * (def_val - atk_val)


            elif move.promotion is not None:
                total_val = BASE_VALUES[move.promotion]/100
            else:
                total_val = 1
            
            values.append(total_val)

            
        return self.softmax(np.array(values)), legal_moves

    # return who's turn to play. chess.WHITE = True, chess.BLACK = false
    def get_turn(self):
        return self.turn
    
    # output what the board currently looks like
    def print(self):
        print(self)

    def eval(self):
        material_imbalance = self.tapered_eval()
        return material_imbalance


    def get_num_pieces(self):
        # get pawn counts
        wp = len(self.pieces(chess.PAWN, chess.WHITE))
        bp = len(self.pieces(chess.PAWN, chess.BLACK))
        
        # get knight counts
        wn = len(self.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(self.pieces(chess.KNIGHT, chess.BLACK))

        # get bishop counts
        wb = len(self.pieces(chess.BISHOP, chess.WHITE))
        bb = len(self.pieces(chess.BISHOP, chess.BLACK))

        # get rook counts
        wr = len(self.pieces(chess.ROOK, chess.WHITE))
        br = len(self.pieces(chess.ROOK, chess.BLACK))

        # get queen counts
        wq = len(self.pieces(chess.QUEEN, chess.WHITE))
        bq = len(self.pieces(chess.QUEEN, chess.BLACK))
        
        return (
            (wp, P_PHASE), 
            (bp, P_PHASE), 
            (wn, N_PHASE), 
            (bn, N_PHASE), 
            (wb, B_PHASE), 
            (bb, B_PHASE), 
            (wr, R_PHASE), 
            (br, R_PHASE), 
            (wq, Q_PHASE), 
            (bq, Q_PHASE)
        )
    
    def get_phase(self):
        phase = TOTAL_PHASE
        pieces = self.get_num_pieces()
        
        for num_pieces, phase_val in pieces:
            # more pieces = lower phase value
            # higher phase value = closer to endgame
            phase -= num_pieces * phase_val

        phase = (phase/TOTAL_PHASE) # scale with highest possible phase value
        return phase
    
    def evaluate_piece(self, piece, square, phase):
        mg_score = 0
        eg_score = 0
        if piece.color == chess.WHITE:
            mg_score = MG_MAP[piece.piece_type][56 ^ square] + MG_VALUES[piece.piece_type]
            eg_score = EG_MAP[piece.piece_type][56 ^ square] + EG_VALUES[piece.piece_type]
        else:
            mg_score = MG_MAP[piece.piece_type][square] + MG_VALUES[piece.piece_type]
            eg_score = EG_MAP[piece.piece_type][square] + EG_VALUES[piece.piece_type]
        
        return mg_score * (1 - phase) + eg_score * (phase)

    # return a static evaluation of the current position
    def tapered_eval(self):
        phase = self.get_phase()

        material_counts = {
            chess.WHITE : 0,
            chess.BLACK : 0
        }
        
        # python-chess defines A1 as 0, H8 as 63
        for square in range(64):
            piece = self.piece_at(square)
            if piece is None: # skip trying to evaluate empty squares
                continue
            piece_val = self.evaluate_piece(piece, square, phase)
            if piece.color == chess.WHITE:
                material_counts[chess.WHITE] += piece_val
            else:
                material_counts[chess.BLACK] += piece_val
        
        return material_counts[chess.WHITE] - material_counts[chess.BLACK]
            
            