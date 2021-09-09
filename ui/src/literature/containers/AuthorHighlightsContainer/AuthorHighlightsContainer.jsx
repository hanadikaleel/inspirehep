import { connect } from 'react-redux';

import { getHighlightedRecords } from '../../../actions/literature';
import AuthorHighlights from '../../components/AuthorHighlights';

const stateToProps = (state, { namespace }) => ({
  results: state.search.getIn(['namespaces', namespace, 'results']),
});

const dispatchToProps = (dispatch) => ({
  onHighlightsLoad(authorId) {
    dispatch(getHighlightedRecords(authorId));
  },
});

export default connect(stateToProps, dispatchToProps)(AuthorHighlights);
